from django.utils.translation import gettext_lazy as _

from pretix.base.plugins import PluginConfig

from . import __version__


class PluginApp(PluginConfig):
    name = "pretix_reservation"
    verbose_name = _("Reservation checkout")

    class PretixPluginMeta:
        name = _("Reservation checkout")
        author = "Jan Pohanka"
        description = _("Allow customers to reserve an order without selecting a payment method.")
        category = "FEATURE"
        visible = True
        version = __version__
        compatibility = "pretix>=2026.6.0.dev0"
        settings_links = [
            ((_('Settings'), _('Reservation checkout')), 'plugins:pretix_reservation:settings', {}),
        ]

    def ready(self):
        from . import signals  # noqa
