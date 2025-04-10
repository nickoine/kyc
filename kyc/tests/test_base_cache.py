from __future__ import annotations

# Internal
from unittest.mock import patch
from .base_test import TestClassBase
from ..common.base_cache import CacheManager


class TestCacheManager(TestClassBase):
    """Unit tests for CacheManager behavior."""

    def setUp(self) -> None:
        super().setUp()
        self.key = "test_key"
        self.value = {"foo": "bar"}
        self.manager = CacheManager()


    @patch("kyc_project.kyc.common.base_cache.caches")
    def test_get_calls_backend(self, mock_caches) -> None:
        """Test that get() retrieves value using correct key from cache backend."""

        # Arrange
        mock_caches.__getitem__.return_value = self.mock_service
        self.mock_service.get.return_value = self.value

        # Act
        result = self.manager.get(self.key)

        # Assert
        mock_caches.__getitem__.assert_called_once_with("default")
        self.mock_service.get.assert_called_once_with(self.key)
        self.assertEqual(result, self.value)


    @patch("kyc_project.kyc.common.base_cache.caches")
    def test_set_calls_backend_with_timeout(self, mock_caches) -> None:
        """Test that set() stores a value with custom timeout in the cache."""

        # Arrange
        mock_caches.__getitem__.return_value = self.mock_service

        # Act
        self.manager.set(self.key, self.value, timeout=300)

        # Assert
        self.mock_service.set.assert_called_once_with(self.key, self.value, 300)


    @patch("kyc_project.kyc.common.base_cache.caches")
    def test_get_or_set_returns_existing(self, mock_caches) -> None:
        """Test that get_or_set() returns cached value if it exists."""

        # Arrange
        mock_caches.__getitem__.return_value = self.mock_service
        self.mock_service.get_or_set.return_value = self.value

        # Act
        result = self.manager.get_or_set(self.key, lambda: {"other": "thing"})

        # Assert
        self.mock_service.get_or_set.assert_called_once()
        self.assertEqual(result, self.value)

    @patch("kyc_project.kyc.common.base_cache.caches")
    def test_get_or_set_calls_default_if_missing(self, mock_caches) -> None:
        """Test that get_or_set() calls default function when key is missing."""

        # Arrange
        mock_caches.__getitem__.return_value = self.mock_service
        self.mock_service.get_or_set.side_effect = lambda key, default, timeout: default()

        # Act
        result = self.manager.get_or_set(self.key, lambda: "computed")

        # Assert
        self.assertEqual(result, "computed")


    @patch("kyc_project.kyc.common.base_cache.caches")
    def test_delete_calls_backend(self, mock_caches) -> None:
        """Test that delete() removes a key from the cache backend."""

        # Arrange
        mock_caches.__getitem__.return_value = self.mock_service

        # Act
        self.manager.delete(self.key)

        # Assert
        self.mock_service.delete.assert_called_once_with(self.key)


    @patch("kyc_project.kyc.common.base_cache.caches")
    def test_incr_existing_value(self, mock_caches) -> None:
        """Test that incr() increases the value of a key if it exists."""

        # Arrange
        mock_caches.__getitem__.return_value = self.mock_service
        self.mock_service.incr.return_value = 5

        # Act
        result = self.manager.incr(self.key)

        # Assert
        self.mock_service.incr.assert_called_once_with(self.key, delta=1)
        self.assertEqual(result, 5)


    @patch("kyc_project.kyc.common.base_cache.caches")
    def test_incr_sets_initial_value_on_error(self, mock_caches) -> None:
        """Test that incr() sets key to 1 if it doesn't exist and raises ValueError."""

        # Arrange
        mock_caches.__getitem__.return_value = self.mock_service
        self.mock_service.incr.side_effect = ValueError("Missing key")

        # Act
        result = self.manager.incr(self.key)

        # Assert
        self.mock_service.set.assert_called_once_with(self.key, 1, 900)
        self.assertEqual(result, 1)


    @patch("kyc_project.kyc.common.base_cache.caches")
    def test_clear_calls_backend(self, mock_caches) -> None:
        """Test that clear() clears all entries from the cache backend."""

        # Arrange
        mock_caches.__getitem__.return_value = self.mock_service

        # Act
        self.manager.clear()

        # Assert
        self.mock_service.clear.assert_called_once()
