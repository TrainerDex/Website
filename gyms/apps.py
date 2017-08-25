from django.apps import AppConfig


class GymsConfig(AppConfig):
    name = 'gyms'

    def ready(self):
        import gyms.signals
