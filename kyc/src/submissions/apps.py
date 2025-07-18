from django.apps import AppConfig


class SubmissionsConfig(AppConfig):

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kyc.src.submissions'

    def ready(self) -> None:
        """ It ensures models are imported only after Django is fully set up. """
        from . import get_submission_model
        get_submission_model()
