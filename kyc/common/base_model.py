# External
from django.db import models, transaction


class BaseManager(models.Manager):
    """Custom manager for common query operations."""


class BaseModel(models.Model):
    """Abstract base model with common CRUD logic."""

    #objects = BaseManager()


    class Meta:
        abstract = True
