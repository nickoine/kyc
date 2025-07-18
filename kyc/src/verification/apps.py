from django.apps import AppConfig

class VerifConfig(AppConfig):

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kyc.src.verification'

    def ready(self) -> None:
        """ It ensures models are imported only after Django is fully set up. """
        from . import get_models
        get_models()
