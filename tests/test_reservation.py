from datetime import timedelta
from decimal import Decimal

from bs4 import BeautifulSoup
from django.test import TestCase
from django.utils.timezone import now
from django_scopes import scopes_disabled

from pretix.base.models import (
    CartPosition, Event, Item, Order, OrderPayment, Organizer, Quota,
)
from pretix.testutils.sessions import get_cart_session_key


class ReservationCheckoutTest(TestCase):
    @scopes_disabled()
    def setUp(self):
        self.organizer = Organizer.objects.create(
            name="Reservation Organizer", slug="reservation-organizer",
            plugins="pretix.plugins.banktransfer",
        )
        self.event = Event.objects.create(
            organizer=self.organizer,
            name="Reservation Event",
            slug="reservation-event",
            date_from=now() + timedelta(days=100),
            plugins="pretix.plugins.banktransfer,pretix_reservation",
            live=True,
        )
        self.event.settings.attendee_names_asked = False
        self.event.settings.payment_banktransfer__enabled = True
        self.event.settings.payment_term_mode = "minutes"
        self.event.settings.payment_term_minutes = 60
        self.quota = Quota.objects.create(event=self.event, name="Tickets", size=1)
        self.item = Item.objects.create(
            event=self.event, name="Ticket", default_price=Decimal("23.00"), admission=True
        )
        self.quota.items.add(self.item)
        self.client.get(f"/{self.organizer.slug}/{self.event.slug}/")
        self.cart_id = get_cart_session_key(self.client, self.event)

    @scopes_disabled()
    def add_ticket(self):
        return CartPosition.objects.create(
            event=self.event,
            cart_id=self.cart_id,
            item=self.item,
            price=Decimal("23.00"),
            expires=now() + timedelta(minutes=10),
        )

    def complete_questions(self):
        return self.client.post(
            f"/{self.organizer.slug}/{self.event.slug}/checkout/questions/",
            {"email": "customer@example.org", "transmission_type": "email"},
            follow=False,
        )

    def enable_reservations(self):
        self.event.settings.reservation_enabled = True

    def test_disabled_keeps_standard_payment_step(self):
        self.add_ticket()
        response = self.complete_questions()
        self.assertRedirects(
            response,
            f"/{self.organizer.slug}/{self.event.slug}/checkout/payment/",
            fetch_redirect_response=False,
        )

    def test_pay_online_keeps_standard_payment_step(self):
        self.enable_reservations()
        self.add_ticket()
        response = self.complete_questions()
        self.assertRedirects(
            response,
            f"/{self.organizer.slug}/{self.event.slug}/checkout/payment/",
            fetch_redirect_response=False,
        )
        response = self.client.get(response.url)
        content = response.content.decode()
        assert "Bank transfer" in content
        assert "Reserve and pay later" in content

    def test_no_enabled_provider_skips_payment_step(self):
        self.enable_reservations()
        self.event.settings.payment_banktransfer__enabled = False
        self.add_ticket()
        response = self.complete_questions()
        self.assertRedirects(
            response,
            f"/{self.organizer.slug}/{self.event.slug}/checkout/confirm/",
            fetch_redirect_response=False,
        )

    def test_reservation_skips_payment_and_shows_confirmation_notice(self):
        self.enable_reservations()
        self.add_ticket()
        response = self.client.post(
            self.complete_questions().url,
            {"payment": "__no_payment__"},
        )
        self.assertRedirects(
            response,
            f"/{self.organizer.slug}/{self.event.slug}/checkout/confirm/",
            fetch_redirect_response=False,
        )
        response = self.client.get(
            f"/{self.organizer.slug}/{self.event.slug}/checkout/confirm/"
        )
        assert "unpaid reservation" in response.content.decode()

    @scopes_disabled()
    def test_reservation_order_and_later_payment_use_standard_lifecycle(self):
        self.enable_reservations()
        self.add_ticket()
        payment_url = self.complete_questions().url
        self.client.post(
            payment_url,
            {"payment": "__no_payment__"},
        )
        response = self.client.post(
            f"/{self.organizer.slug}/{self.event.slug}/checkout/confirm/",
            follow=True,
        )
        assert BeautifulSoup(response.content, "lxml").select(".thank-you")

        order = Order.objects.get()
        assert order.status == Order.STATUS_PENDING
        assert order.payments.count() == 0
        assert order.positions.count() == 1
        assert self.quota.availability() == (Quota.AVAILABILITY_ORDERED, 0)
        assert timedelta(minutes=55) < order.expires - order.datetime <= timedelta(minutes=60)
        assert order.event.settings.payment_term_minutes == 60

        pay_url = (
            f"/{self.organizer.slug}/{self.event.slug}/order/"
            f"{order.code}/{order.secret}/pay/change"
        )
        response = self.client.get(pay_url)
        assert "Bank transfer" in response.content.decode()
        response = self.client.post(pay_url, {"payment": "banktransfer"})
        assert response.status_code == 302
        payment = order.payments.get()
        assert payment.provider == "banktransfer"
        assert payment.state == OrderPayment.PAYMENT_STATE_CREATED

        payment.confirm()
        order.refresh_from_db()
        assert order.status == Order.STATUS_PAID
