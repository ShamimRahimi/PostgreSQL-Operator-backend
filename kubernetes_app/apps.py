from django.apps import AppConfig


class KubernetesAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kubernetes_app'
