# pretix reservation

This plugin lets customers choose between paying during checkout and creating an unpaid reservation. Reservations use
the normal pretix pending-order model and do not create a fake payment or any `OrderPayment` object. A regular payment
can be initiated later from the standard order page.

Enable it for the event, then configure it under **Settings → Reservation
checkout**. Expiry is part of the normal pending-order lifecycle: capacity is
released only when Pretix's periodic processing changes the order to `expired`.
