# pretix reservation

This plugin lets customers choose between paying during checkout and creating an unpaid reservation. Reservations use
the normal pretix pending-order model and do not create a fake payment or any `OrderPayment` object. A regular payment
can be initiated later from the standard order page.
