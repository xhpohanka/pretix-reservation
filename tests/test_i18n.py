from django.utils.translation import gettext, override


def test_czech_translation_is_shipped():
    with override("cs"):
        assert gettext("Pay online") == "Zaplatit online"
        assert gettext("Reserve and pay later") == "Rezervovat a zaplatit později"
        assert gettext(
            "Create an unpaid reservation. You can choose a payment method later."
        ) == "Vytvořte nezaplacenou rezervaci. Platební metodu můžete vybrat později."
