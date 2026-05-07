from django.apps import AppConfig


class TablenameConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tablename'

    def ready(self):
        from . import signals  # noqa: F401
