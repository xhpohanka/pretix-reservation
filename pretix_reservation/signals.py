from django.dispatch import receiver
from django.template.loader import get_template

from pretix.base.signals import order_expiry
from pretix.presale.signals import (
    checkout_confirm_page_content, checkout_payment_required,
)
from pretix.presale.checkoutflow import PAYMENT_SELECTION_SKIPPED
from pretix.presale.views.cart import cart_session

from .checkout import reservation_enabled, reservation_expiry


@receiver(order_expiry, dispatch_uid="pretix_reservation_order_expiry")
def unpaid_reservation_expiry(sender, order, subevents=None, payments=None, **kwargs):
    # ``None`` means the caller cannot tell us how the order was created.
    # Only an explicitly empty checkout payment list identifies this plugin's
    # "reserve now, choose payment later" path. Normal web orders with a
    # pending bank-transfer payment must keep the standard payment term.
    if payments is None or payments or not reservation_enabled(sender):
        return None

    if sender.has_subevents:
        dates = [se for se in (subevents or []) if se is not None]
        if dates and not hasattr(dates[0], "date_from"):
            dates = list(sender.subevents.filter(pk__in=dates))
        if not dates:
            return None
        first_date = min(dates, key=lambda se: se.date_from)
    else:
        first_date = sender

    return reservation_expiry(sender).datetime(first_date)


@receiver(checkout_payment_required, dispatch_uid="pretix_reservation_payment_required")
def payment_required(sender, request, **kwargs):
    if reservation_enabled(sender):
        return False


@receiver(checkout_confirm_page_content, dispatch_uid="pretix_reservation_confirm_notice")
def confirmation_notice(sender, request, **kwargs):
    if reservation_enabled(sender) and cart_session(request).get(PAYMENT_SELECTION_SKIPPED):
        return get_template("pretix_reservation/confirm_notice.html").render({}, request=request)
