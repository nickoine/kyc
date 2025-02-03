# External
from django.db import models

# Roles Table
class Role(models.Model):

    role_name = models.CharField(max_length=50, unique=True)  # Name of the role (e.g., admin, user, etc.)
    role_description = models.TextField(blank=True, null=True)  # Optional description of the role
    role_created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the role was created
    role_updated_at = models.DateTimeField(auto_now=True)  # Timestamp when the role was last updated

    def __str__(self):
        return self.role_name

# Roles-User Table
class UserRole(models.Model):

    role = models.ForeignKey(Role, on_delete=models.CASCADE)  # Relationship to Role table
    user = models.ForeignKey('User', on_delete=models.CASCADE)  # Relationship to User table
