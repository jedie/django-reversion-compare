from django.apps import AppConfig as BaseAppConfig


class AppConfig(BaseAppConfig):
    name = 'reversion_compare'
    verbose_name = 'reversion_compare'

    def ready(self):
        import reversion_compare.checks  # noqa
