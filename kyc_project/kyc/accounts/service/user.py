import random
import string

from django.contrib.auth.models import BaseUserManager

from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    pass

class UserManager(BaseUserManager):

    def create_user(self, email: str, password: Optional[str] = None, **extra_fields):

        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        if "username" not in extra_fields or not extra_fields.get("username"):
            extra_fields["username"] = self.generate_username(email)  # Generate a default username if not provided
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        # user.save(using=self._db)
        return user


    def create_superuser(self, email: str, password: Optional[str] = None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

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
