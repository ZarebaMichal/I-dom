from django.apps import AppConfig


class RegisterConfig(AppConfig):
    name = 'register'
    # Importing singals to run by python interpreter
    def ready(self):
        import register.signals