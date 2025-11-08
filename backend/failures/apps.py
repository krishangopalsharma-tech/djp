from django.apps import AppConfig

class FailuresConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "failures"

    def ready(self):
        # Import signals here to register them
        import failures.models
