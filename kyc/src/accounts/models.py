# External
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator

# Internal
from ...common.base_model import BaseModel
from .service import UserManager


class User(BaseModel, AbstractUser):
    """
    Custom user model representing system users.
    Uses email as the primary identifier instead of username.
    """

    username = None

    # Authentication fields
    email = models.EmailField(
        _('email_address'),
        unique=True,
        help_text=_('The unique email address used for authentication.'),
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )
    # Registration metadata
    registration_method = models.CharField(
        _('registration_method'),
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('google', 'Google'),
            ('facebook', 'Facebook'),
            ('apple', 'AppleID')
        ],
        default='email',
        help_text=_('Method used for account registration.')
    )

    date_joined = models.DateTimeField(
        _('date_joined'),
        auto_now_add=True,
        help_text=_('Timestamp when the user was created.')
    )

    # Required fields for createsuperuser
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()


    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['email']
        indexes = [
            models.Index(fields=['email']),
        ]


    def __str__(self) -> str:
        return f"User {self.email or '[unsaved]'} via {self.registration_method or '[unknown]'}"


    def clean(self) -> None:
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)


    @property
    def group_names(self) -> str:
        return ", ".join(self.groups.values_list("name", flat=True))


class Account(models.Model):
    """
    Represents a verified user account in the system.
    Each account is uniquely tied to a single user and tracks verification status.
    """

    user = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        related_name='account',
        verbose_name=_("User"),
        help_text=_("The single user associated with this account.")
    )
    account_username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        db_index=True,
        validators=[MinLengthValidator(3)],
        help_text=_("Unique public identifier for this account (3-150 characters).")
    )
    verified = models.BooleanField(
        _("verified_status"),
        default=False,
        db_index = True,
        help_text=_("Designates whether this account passed verification checks.")
    )
    verification_date = models.DateTimeField(
        _("verification_timestamp"),
        null=True,
        blank=True,
        help_text=_("When verification was completed (auto-set when verified=True).")
    )
    created_at = models.DateTimeField(
        _("created_at"),
        auto_now_add=True,
        help_text=_("When this account was first registered.")
    )
    updated_at = models.DateTimeField(
        _("updated_at"),
        auto_now=True,
        help_text=_("When this account was last modified.")
    )
    last_login = models.DateTimeField(
        _("last_login"),
        null=True,
        blank=True,
        help_text=_("Most recent authenticated access to this account.")
    )


    class Meta:
        verbose_name = _("Account")
        verbose_name_plural = _("Accounts")
        ordering = ['account_username']
        # constraints = [
        #     models.CheckConstraint(
        #         check=models.Q(verified=False) | models.Q(verification_date__isnull=False),
        #         name="verified_has_date"
        #     )
        # ]
        indexes = [
            models.Index(fields=['account_username', 'verified']) # Composite index
        ]
        permissions = [
            ("can_verify_account", "Can manually verify accounts"),
            ("can_suspend_account", "Can suspend or deactivate accounts"),
        ]


    def __str__(self) -> str:
        return f"{self.account_username} ({'Verified' if self.verified else 'Unverified'})."


    def clean(self) -> None:
        """Validate verification logic before saving."""

        super().clean()
        if self.verified and not self.verification_date:
            self.verification_date = timezone.now()
        raise ValidationError({
            'verification_date': _("Verification date can be set after account is verified.")
        })


    @property
    def age_days(self) -> int:
        """Calculate account age in days."""
        return (timezone.now() - self.created_at).days if self.created_at else None
