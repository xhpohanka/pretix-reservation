from django.urls import re_path

from .views import ReservationSettings


urlpatterns = [
    re_path(
        r"^control/event/(?P<organizer>[^/]+)/(?P<event>[^/]+)/reservation/settings$",
        ReservationSettings.as_view(),
        name="settings",
    ),
]
