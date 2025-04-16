# External

# Internal
from typing import Type
from unittest.mock import patch, MagicMock

from .base_test import TestClassBase, ModelTest
from kyc.common.base_repo import BaseRepository


# class TestableRepo(BaseRepository[ModelTest]):
#
#     @property
#     def model(self) -> Type[ModelTest]:
#         return ModelTest


class TestBaseRepoGet(TestClassBase):


    def setUp(self) -> None:
        super().setUp()

        self.test_data = 1
        self.repository = BaseRepository(model=self.real_test_model_as_class)
        self.repository._manager = self.mock_service
        self.repository._cache_manager = self.mock_service


        self.repository._cache_enabled = False


    def test_get_entity_by_id_without_cache_success(self):
        """Test successful fetch when cache is disabled."""

        # Arrange
        self.repository.manager.get_by_id.return_value = self.mock_model

        # Act
        result = self.repository.get_entity_by_id(self.test_data)

        # Assert
        self.assertEqual(result, self.mock_model)
        self.mock_cache.get.assert_not_called()
        self.mock_cache.set.assert_not_called()
        self.assert_no_errors_logged()


    def test_get_entity_by_id_without_cache_failed(self):
        """Test failed fetch when cache is disabled."""

        # Arrange
        self.repository.manager.get_by_id.return_value = None

        # Act
        result = self.repository.get_entity_by_id(self.test_data)

        # Assert
        self.assertEqual(result, None)
        self.mock_cache.get.assert_not_called()
        self.mock_cache.set.assert_not_called()
        self.assert_no_errors_logged()


    def test_get_entity_by_id_without_cache_exception(self):
        """Test failed fetch when cache is disabled and exception occurs"""

        # Arrange
        self.repository.manager.get_by_id.side_effect = Exception("DB error")

        # Act
        with patch("kyc.common.base_repo.logger.exception") as mock_logger:
            result = self.repository.get_entity_by_id(self.test_data)

        # Assert
        self.assertIsNone(result)
        mock_logger.assert_called_once()
        self.assertIn("Failed to fetch", mock_logger.call_args[0][0])
        self.assertIn(str(self.test_data), mock_logger.call_args[0][0])
        self.mock_cache.get.assert_not_called()


    def test_get_entity_by_id_with_cache_hit(self):
        """Test that get_entity_by_id() returns cached value and skips DB on cache hit."""

        # Arrange
        self.repository._cache_enabled = True

        expected_result = MagicMock()
        self.repository._cache_manager.get = MagicMock(return_value=expected_result)
        self.repository._cache_manager.set = MagicMock()
        self.repository._manager.get_by_id = MagicMock()

        # Act
        result = self.repository.get_entity_by_id(self.test_data)
        expected_key = f"{self.repository.model.__name__.lower()}:{self.test_data}"

        # Assert
        self.assertEqual(result, expected_result)
        self.repository._cache_manager.get.assert_called_once_with(expected_key)
        self.repository._manager.get_by_id.assert_not_called()
        self.repository._cache_manager.set.assert_not_called()


    def test_get_entity_by_id_cache_miss_hits_db_and_sets_cache(self):
        """Test that get_entity_by_id() hits DB and sets cache when cache is enabled but misses."""

        # Arrange
        self.repository._cache_enabled = True

        expected_result = self.mock_service
        self.repository._cache_manager.set = MagicMock()
        self.repository._cache_manager.get = MagicMock(return_value=None)
        self.repository._manager.get_by_id = MagicMock(return_value=expected_result)

        # Act
        result = self.repository.get_entity_by_id(self.test_data)
        expected_key = f"{self.repository.model.__name__.lower()}:{self.test_data}"

        # Assert
        self.assertEqual(result, expected_result)
        self.repository._cache_manager.get.assert_called_once_with(expected_key)
        self.repository._manager.get_by_id.assert_called_once_with(self.test_data)
        self.repository._cache_manager.set.assert_called_once_with(
            expected_key, expected_result, timeout=self.repository.CACHE_TIMEOUT
        )


class TestBaseRepoCreate(TestClassBase):


    def setUp(self) -> None:
        super().setUp()

        self.test_data = 1
        self.repository = BaseRepository(model=self.real_test_model_as_class)
        self.repository._manager = self.mock_service
        self.repository._cache_manager = self.mock_service

        self.repository._cache_enabled = False


    def test_create_entity_delete_cache_success(self):
        """Should create an entity and invalidate cache successfully."""

        # Arrange
        self.repository._cache_enabled = True
        self.mock_service.id = 2

        self.repository._manager.create_instance = MagicMock(return_value=self.mock_service)
        self.repository._cache_manager.delete = MagicMock()

        # Act
        result = self.repository.create_entity(name="Test")

        # Assert
        self.assertEqual(result, self.mock_service)
        expected_key = f"{self.repository.model.__name__.lower()}:{self.mock_service.id}"
        self.repository._cache_manager.delete.assert_called_once_with(expected_key)


    def test_create_entity_fail_and_handles_error(self):
        """Should log exception and not call cache when create_instance raises error."""

        # Arrange
        self.repository._cache_enabled = True
        self.repository._manager.create_instance = MagicMock(side_effect=Exception("Unexpected error"))
        self.repository._cache_manager.delete = MagicMock()

        with patch("kyc.common.base_repo.logger.exception") as mock_logger:
            # Act
            result = self.repository.create_entity(name="Test")

            # Assert
            self.assertIsNone(result)
            mock_logger.assert_called_once()
            self.assertIn("Unexpected error", mock_logger.call_args[0][0])
            self.repository._cache_manager.delete.assert_not_called()


    def test_bulk_create_entities_success(self):
        """Should bulk create entities and invalidate cache successfully."""

        pass


    def test_bulk_create_entities_fail_and_handle_error(self):
        """Should bulk create entities and invalidate cache successfully."""

        pass



class TestBaseRepoUpdate(TestClassBase):


    def setUp(self) -> None:
        super().setUp()

        self.test_data = 1
        self.repository = BaseRepository(model=self.real_test_model_as_class)
        self.repository._manager = self.mock_service
        self.repository._cache_manager = self.mock_service

        self.repository._cache_enabled = False


    def test_update_entity_delete_cache_success(self):
        """Should update an entity and invalidate cache successfully."""

        pass

    def test_update_entity_fail_and_handles_error(self):
        """Should log exception and not call cache when update_instance raises error."""

        pass

    def test_bulk_update_entities_success(self):
        """Should bulk update entities and invalidate cache successfully."""

        pass


    def test_bulk_update_entities_fail_and_handles_error(self):
        """Should bulk update entities and invalidate cache successfully."""

        pass


class TestBaseRepoDelete(TestClassBase):

    def setUp(self) -> None:
        super().setUp()

        self.test_data = 1
        self.repository = BaseRepository(model=self.real_test_model_as_class)
        self.repository._manager = self.mock_service
        self.repository._cache_manager = self.mock_service

        self.repository._cache_enabled = False


    def test_delete_entity_delete_cache_success(self):
        """Should delete an entity and clear cache successfully."""

        pass

    def test_update_entity_fail_and_handles_error(self):
        """Should log exception and not call cache when delete_instance raises error."""

        pass


    def test_bulk_delete_entities_success(self):
        """Should bulk delete entities and clear cache successfully."""

        pass


    def test_bulk_delete_entities_fail_and_handles_error(self):
        """Should bulk update entities and invalidate cache successfully."""

        pass

