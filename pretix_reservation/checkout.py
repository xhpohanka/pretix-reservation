def reservation_enabled(event):
    return event.settings.get("reservation_enabled", default=False, as_type=bool)
