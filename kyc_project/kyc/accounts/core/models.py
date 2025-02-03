# Internal
from ..service import UserManager
from ... import Role

# External
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, Group, Permission

class User(AbstractBaseUser, PermissionsMixin):

    user_email = models.EmailField(unique=True)  # Unique email for user identification
    user_account = models.OneToOneField('Account', on_delete=models.CASCADE, null=True, blank=True)  # Links user to account
    user_created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for account creation
    user_is_active = models.BooleanField(default=True)  # Indicates if the user is active
    objects = UserManager()

    USERNAME_FIELD = 'email'  # Email is the unique identifier for authentication

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_groups',  # Custom related name
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions',  # Custom related name
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.user_email


class Account(models.Model):

    account_user = models.OneToOneField(User, on_delete=models.CASCADE)  # Links account to a User
    account_admin = models.BooleanField(default=False)  # Flag to indicate if this is an admin account
    account_role = models.ForeignKey(Role, on_delete=models.CASCADE)  # Role assigned to the account
    account_questionnaires = models.ManyToManyField('Questionnaire', related_name='accounts')  # Questionnaires associated with the account
    account_username = models.CharField(max_length=150, unique=True)  # Unique username for the account
    account_name = models.CharField(max_length=100)  # Account holder's first name
    account_surname = models.CharField(max_length=100)  # Account holder's surname
    account_mobile = models.CharField(max_length=15, blank=True, null=True)  # Mobile number (optional)
    account_verified = models.BooleanField(default=False)  # Indicates if the account is verified
    account_created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for account creation
    account_updated_at = models.DateTimeField(auto_now=True)  # Timestamp for last account update
    account_last_login = models.DateTimeField(null=True, blank=True)  # Tracks the last login of the account

    def __str__(self):
        return self.account_username


class Admin(models.Model):

    admin_user = models.OneToOneField(User, on_delete=models.CASCADE)  # Links admin to a User
    admin_account = models.OneToOneField('Account', on_delete=models.CASCADE)  # Links admin to an Account
    role = models.ForeignKey(Role, on_delete=models.CASCADE)  # Role assigned to the admin
    admin_username = models.CharField(max_length=150, unique=True)  # Unique username for the admin
    admin_created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for admin creation
    admin_last_login = models.DateTimeField(null=True, blank=True)  # Tracks the last login of the admin

    def __str__(self):
        return self.admin_username
