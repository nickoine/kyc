from django.apps import AppConfig


class UserResponsesConfig(AppConfig):

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kyc.src.responses'

    def ready(self) -> None:
        """ It ensures models are imported only after Django is fully set up. """
        from . import get_user_response_model
        get_user_response_model()
