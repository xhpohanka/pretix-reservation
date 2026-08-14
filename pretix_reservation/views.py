from django.urls import reverse

from pretix.base.models import Event
from pretix.control.views.event import EventSettingsFormView, EventSettingsViewMixin

from .forms import ReservationSettingsForm


class ReservationSettings(EventSettingsViewMixin, EventSettingsFormView):
    model = Event
    form_class = ReservationSettingsForm
    template_name = "pretix_reservation/settings.html"
    permission = "event.settings.general:write"

    def get_success_url(self):
        return reverse("plugins:pretix_reservation:settings", kwargs={
            "organizer": self.request.event.organizer.slug,
            "event": self.request.event.slug,
        })
