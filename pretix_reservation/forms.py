from django import forms
from django.utils.translation import gettext_lazy as _

from pretix.base.forms import SettingsForm


class ReservationSettingsForm(SettingsForm):
    reservation_enabled = forms.BooleanField(
        label=_("Enable reservation without payment"),
        help_text=_(
            "Customers can choose to create a pending reservation and select a payment method later."
        ),
        required=False,
    )
