from django.apps import AppConfig

class BrewlabConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'brewlab'

    def ready(self):
        import brewlab.signals  #подключаем сигналы

