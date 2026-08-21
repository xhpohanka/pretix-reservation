from django import forms
from django.utils.translation import gettext_lazy as _

from pretix.base.forms import SettingsForm
from pretix.base.reldate import RelativeDateTimeField

from .checkout import reservation_expiry


class ReservationSettingsForm(SettingsForm):
    reservation_enabled = forms.BooleanField(
        label=_("Enable reservation without payment"),
        help_text=_(
            "Customers can choose to create a pending reservation and select a payment method later."
        ),
        required=False,
    )
    reservation_expiry = RelativeDateTimeField(
        label=_("Reservation validity"),
        help_text=_(
            "An unpaid reservation expires at this time relative to the start of the earliest "
            "date included in the order. Choosing a payment method later does not extend it."
        ),
        limit_choices=("date_from",),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.initial.get("reservation_expiry"):
            self.initial["reservation_expiry"] = reservation_expiry(self.obj)
