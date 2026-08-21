from pretix.base.reldate import RelativeDate, RelativeDateWrapper


EXPIRY_SETTING = "reservation_expiry"


def reservation_enabled(event):
    return event.settings.get("reservation_enabled", default=False, as_type=bool)


def default_reservation_expiry():
    return RelativeDateWrapper(RelativeDate(
        days=0,
        minutes=0,
        time=None,
        is_after=False,
        base_date_name="date_from",
    ))


def reservation_expiry(event):
    value = event.settings.get(EXPIRY_SETTING, default=None)
    return RelativeDateWrapper.from_string(value) if value else default_reservation_expiry()
