# External
from django.db import IntegrityError, DatabaseError, models
from django.core.cache import cache

# Internal
import re
from typing import Type, Optional, List
from unittest.mock import patch, MagicMock, call

from ..base_test import TestClassBase
from ..base_model import BaseModel
from ..base_repo import BaseRepository


class TestBaseRepoGet(TestClassBase):


    def setUp(self) -> None:
        super().setUp()

        self.repository = BaseRepository(model=self.test_model)

        # Clear cache before each test
        cache.clear()


    def test_get_entity_by_id_without_cache(self):
        """Test get_entity_by_id without caching."""
        # Setup
        test_id = 1
        mock_instance = MagicMock(spec=self.test_model)
        self.repository.manager.get_by_id.return_value = mock_instance

        # Execute
        result = self.repository.get_entity_by_id(test_id)

        # Verify
        self.repository.manager.get_by_id.assert_called_once_with(test_id)
        self.assertEqual(result, mock_instance)
        self.assert_no_errors_logged()

        # Verify cache wasn't used
        self.mock_cache.get.assert_not_called()
        self.mock_cache.set.assert_not_called()


class TestBaseRepoCreate(TestClassBase):
    pass


class TestBaseRepoUpdate(TestClassBase):
    pass


class TestBaseRepoDelete(TestClassBase):
    pass

