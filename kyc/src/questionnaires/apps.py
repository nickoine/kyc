from django.apps import AppConfig

class QuestionnairesConfig(AppConfig):

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kyc.src.questionnaires'

    def ready(self) -> None:
        """ It ensures models are imported only after Django is fully set up. """
        from . import get_questionnaires_models
        get_questionnaires_models()
