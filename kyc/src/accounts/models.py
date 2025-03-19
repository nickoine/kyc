# External
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin, Group, Permission

# Internal
from ...common.base_model import BaseModel
from ...etc import AUTH_USER_MODEL
from .service import UserManager


class User(AbstractUser, PermissionsMixin):
    """
    Represents a user in the system.
    Each user has a unique email address and is linked to a single account.
    """

    user_email = models.EmailField(
        unique=True,
        verbose_name="Email",
        help_text="The unique email address used for authentication.",
        db_index=True  # Index for faster lookups
    )
    user_account = models.OneToOneField(
        'Account',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Account",
        help_text="The account associated with this user."
    )
    user_created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
        help_text="The timestamp when the user was created."
    )

    USERNAME_FIELD = 'user_email'
    objects = UserManager()

    # Groups and Permissions (required for Django's auth system)
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="custom_user_groups",  # Custom related name to avoid clashes
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="custom_user_permissions",  # Custom related name to avoid clashes
        related_query_name="user",
    )

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['user_email']

    def __str__(self):
        return self.user_email


class Role(BaseModel):
    """
    Represents a role in the system.
    Each role can be assigned to multiple accounts.
    """
    role_name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Role Name",
        help_text="The name of the role (e.g., admin, user).",
        db_index=True  # Index for faster lookups
    )
    role_description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description",
        help_text="An optional description of the role."
    )
    role_created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
        help_text="The timestamp when the role was created."
    )
    role_updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
        help_text="The timestamp when the role was last updated."
    )

    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"
        ordering = ['role_name']

    def __str__(self):
        return self.role_name


class Account(BaseModel):
    """
    Represents a user account in the system.
    Each account is linked to a single user and has a role.
    """
    account_user = models.OneToOneField(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="User",
        help_text="The user associated with this account."
    )
    account_admin = models.BooleanField(
        default=False,
        verbose_name="Is Admin",
        help_text="Indicates whether this account has admin privileges."
    )
    account_role = models.ForeignKey(
        'Role',
        on_delete=models.CASCADE,
        verbose_name="Role",
        help_text="The role assigned to this account.",
        db_index=True  # Index for faster filtering by role
    )
    account_questionnaires = models.ManyToManyField(
        'questionnaires.Questionnaire',
        related_name='accounts',
        verbose_name="Questionnaires",
        help_text="The questionnaires associated with this account."
    )
    account_username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Username",
        help_text="The unique username for this account.",
        db_index=True  # Index for faster lookups
    )
    account_name = models.CharField(
        max_length=100,
        verbose_name="First Name",
        help_text="The first name of the account holder."
    )
    account_surname = models.CharField(
        max_length=100,
        verbose_name="Surname",
        help_text="The surname of the account holder."
    )
    account_mobile = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="Mobile Number",
        help_text="The mobile number of the account holder (optional)."
    )
    account_verified = models.BooleanField(
        default=False,
        verbose_name="Is Verified",
        help_text="Indicates whether the account has been verified."
    )
    account_created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
        help_text="The timestamp when the account was created."
    )
    account_updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
        help_text="The timestamp when the account was last updated."
    )
    account_last_login = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Last Login",
        help_text="The timestamp of the last login for this account."
    )

    class Meta:
        verbose_name = "Account"
        verbose_name_plural = "Accounts"
        ordering = ['account_username']

    def __str__(self):
        return self.account_username


class Admin(BaseModel):
    """
    Represents an admin user in the system.
    Each admin is linked to a single user and account, and has a specific role.
    """
    admin_user = models.OneToOneField(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="User",
        help_text="The user associated with this admin.",
        db_index=True  # Index for faster lookups
    )
    admin_account = models.OneToOneField(
        'Account',
        on_delete=models.CASCADE,
        verbose_name="Account",
        help_text="The account associated with this admin.",
        db_index=True  # Index for faster lookups
    )
    role = models.ForeignKey(
        'Role',
        on_delete=models.CASCADE,
        verbose_name="Role",
        help_text="The role assigned to this admin.",
        db_index=True  # Index for faster filtering by role
    )
    admin_username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Username",
        help_text="The unique username for this admin.",
        db_index=True  # Index for faster lookups
    )
    admin_created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
        help_text="The timestamp when the admin was created."
    )
    admin_last_login = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Last Login",
        help_text="The timestamp of the last login for this admin."
    )

    class Meta:
        verbose_name = "Admin"
        verbose_name_plural = "Admins"
        ordering = ['admin_username']

    def __str__(self):
        return self.admin_username
