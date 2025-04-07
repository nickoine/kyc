from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):

    pass

    # def create_user(self, email: str, password: Optional[str] = None, **extra_fields):
    #
    #     if not email:
    #         raise ValueError("The Email field must be set")
    #
    #     email = self.normalize_email(email)
    #     if "username" not in extra_fields or not extra_fields.get("username"):
    #         extra_fields["username"] = self.generate_username(email)  # Generate a default username if not provided
    #     user = self.model(email=email, **extra_fields)
    #     user.set_password(password)
    #     # user.save(using=self._db)
    #     return user
    #
    #
    # def create_superuser(self, email: str, password: Optional[str] = None, **extra_fields):
    #     extra_fields.setdefault("is_staff", True)
    #     extra_fields.setdefault("is_superuser", True)
    #
    #     if not extra_fields.get("is_staff"):
    #         raise ValueError("Superuser must have is_staff=True.")
    #     if not extra_fields.get("is_superuser"):
    #         raise ValueError("Superuser must have is_superuser=True.")
    #
    #     return self.create_user(email, password, **extra_fields)

    #
    # def generate_username(self, email: str) -> str:
    #     base_username = email.split("@")[0]
    #     username = base_username
    #     retry_count = 0  # Introduce a retry counter to avoid potential infinite loops
    #     max_retries = 100
    #
    #     while self.model.objects.filter(username=username).exists():  # Ensure username uniqueness
    #         if retry_count >= max_retries:
    #             raise RuntimeError("Exceeded maximum retries for generating a unique username")
    #         random_suffix = ''.join(random.choices(string.digits, k=3))
    #         username = f"{base_username}{random_suffix}"
    #         retry_count += 1
    #     return username


# Signal to create an Account when a User is created
# @receiver(post_save, sender=User)
# def create_user_account(sender, instance, created, **kwargs):
#     if created:
#         default_role = Role.objects.get_or_create(role_name='user')[0]
#         Account.objects.create(
#             account_user=instance,
#             account_role=default_role,
#             account_username=instance.user_email  # Use email as username
#         )
# @receiver(post_save, sender=User)
# def assign_default_group(sender, instance, created, **kwargs):
#     if created:
#         default_group, created = Group.objects.get_or_create(name='User')
#         instance.groups.add(default_group)

# # Signal to update account_updated_at when the account is modified
# @receiver(post_save, sender=Account)
# def update_account_updated_at(sender, instance, **kwargs):
#     instance.account_updated_at = timezone.now()
#     instance.save()

# # Signal to update admin_last_login when the associated user logs in
# @receiver(post_save, sender=User)
# def update_admin_last_login(sender, instance, **kwargs):
#     if hasattr(instance, 'admin'):
#         instance.admin.admin_last_login = timezone.now()
#         instance.admin.save()
#
# def promote_to_superadmin(self):
#     self.role = Role.objects.get(role_name='Superadmin')
#     self.save()
#
# def demote_to_user(self):
#     self.role = Role.objects.get(role_name='User')
#     self.save()
#
# def assign_default_group(user):
#     if user.registration_method == 'email':
#         group = Group.objects.get(name='email_users')
#         user.groups.add(group)
