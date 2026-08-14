from django.dispatch import receiver
from django.template.loader import get_template

from pretix.presale.signals import (
    checkout_confirm_page_content, checkout_payment_required,
)
from pretix.presale.checkoutflow import PAYMENT_SELECTION_SKIPPED
from pretix.presale.views.cart import cart_session

from .checkout import reservation_enabled


@receiver(checkout_payment_required, dispatch_uid="pretix_reservation_payment_required")
def payment_required(sender, request, **kwargs):
    if reservation_enabled(sender):
        return False


@receiver(checkout_confirm_page_content, dispatch_uid="pretix_reservation_confirm_notice")
def confirmation_notice(sender, request, **kwargs):
    if reservation_enabled(sender) and cart_session(request).get(PAYMENT_SELECTION_SKIPPED):
        return get_template("pretix_reservation/confirm_notice.html").render({}, request=request)
