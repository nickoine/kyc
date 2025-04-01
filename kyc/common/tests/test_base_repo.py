# External
from django.db import IntegrityError, DatabaseError, models
from django.core.cache import cache

# Internal
import re
from typing import Optional
from unittest.mock import patch, MagicMock
from ..base_test import TestClassBase
from ..base_model import BaseModel
from ..base_repo import BaseRepository


# class BaseModelTest(BaseModel):
#     """Concrete model for testing BaseRepo functionality."""
#
#     name = models.CharField(max_length=255)
#
#     class Meta:
#         app_label = "_"
#         managed = False


class TestBaseRepoGet(TestClassBase):
    pass



class TestBaseRepoCreate(TestClassBase):
    pass


class TestBaseRepoUpdate(TestClassBase):
    pass


class TestBaseRepoDelete(TestClassBase):
    pass


class TestBaseRepoCache(TestClassBase):
    pass
