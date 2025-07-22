# External
from django.db import models
from django.db.models.functions import Lower
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

# Internal
from ...common.base_model import BaseModel
from .service import UserManager


class User(BaseModel, AbstractUser):
    """
    Custom user model representing system users.
    Uses email as the primary identifier instead of username.
    """

    REGISTRATION_CHOICES = [
        ('email', 'Email'),
        ('google', 'Google'),
        ('github', 'GitHub'),
        ('facebook', 'Facebook'),
        ('apple', 'Apple')
    ]

    username = None

    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        related_name='custom_user_groups',
        help_text=_('The groups this user belongs to.')
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        related_name='custom_user_permissions',
        help_text=_('Specific permissions for this user.')
    )

    # Authentication fields
    email = models.EmailField(
        _('email_address'),
        unique=True,
        help_text=_('The unique email address used for authentication.'),
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )

    registration_method = models.CharField(
        max_length=20,
        choices=REGISTRATION_CHOICES,
        help_text=_('Method used for account registration.')
    )

    date_joined = models.DateTimeField(
        _('date_joined'),
        auto_now_add=True,
        help_text=_('Timestamp when the user was created.')
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Metadata"),
        help_text=_("Optional context like browser, device, geolocation, etc.")
    )

    # Required fields for createsuperuser
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()


    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['date_joined']
        indexes = [
            models.Index(fields=['email']),
        ]


    def __str__(self) -> str:
        return f"User {self.email or '[unsaved]'} via {self.registration_method or '[unknown]'}"


    def clean(self) -> None:
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)


class Account(BaseModel):
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

    username = models.CharField(
        max_length=30,
        unique=True,
        verbose_name=_("Username"),
        help_text=_("Public-facing username"),
        validators=[RegexValidator(regex='^[a-zA-Z0-9_]+$')]
    )

    status = models.BooleanField(
        default=False,
        verbose_name=_("Verification status"),
        help_text=_("True = verified, False = unverified")
    )

    is_staff = models.BooleanField(
        default=False,
        verbose_name=_("Staff status"),
        help_text=_("Indicates whether the user has administrative privileges.")
    )

    date_verified = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Verification date")
    )

    date_joined = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date joined")
    )

    group = models.ForeignKey(
        'AccountGroup',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active status")
    )

    last_login = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Last login")
    )


    class Meta:
        verbose_name = _("Account")
        verbose_name_plural = _("Accounts")
        ordering = ['-status', 'username']  # Verified accounts first, then by username

        constraints = [
            # Prevent duplicate usernames case-insensitively
            models.UniqueConstraint(
                Lower('username'),
                name='unique_lower_username'
            )
        ]

        indexes = [
            # Covering index for user lookup performance
            models.Index(
                fields=['username', 'is_active'],
                name='active_user_lookup_idx'
            )
        ]
        # admin
        permissions = [
            ("view_full_account", "Can view all account details"),
            ("change_account_status", "Can modify verification status"),
            ("assign_group","Can assign group to the user's account"),
            # ("suspend_account", "Can deactivate accounts")
        ]


    def __str__(self) -> str:
        return f"{self.username} ({'Verified' if self.status else 'Unverified'})."


    def clean(self) -> None:
        """Validate verification logic before saving."""

        super().clean()
        if self.status and not self.date_verified:
            self.verification_date = timezone.now()
        raise ValidationError({
            'verification_date': _("Verification date can be set after account is verified.")
        })

    @property
    def age_days(self) -> int:
        """Calculate account age in days."""
        return (timezone.now() - self.date_joined).days if self.date_joined else None


class AccountGroup(BaseModel):
    """Dynamic user's account group (e.g., IT, Blogger, Other), can be assigned after verification."""

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
