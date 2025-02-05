from django.apps import AppConfig


class AccountsConfig(AppConfig):

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kyc.src.accounts'

    def ready(self) -> None:
        """ It ensures models are imported only after Django is fully set up. """
        from . import get_accounts_models
        get_accounts_models()
