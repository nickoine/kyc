# External
import pytest
from unittest.mock import MagicMock

# Internal
from ..base_model import BaseManager


class MockBaseManager(BaseManager):
    """Test double for BaseManager."""

    def __init__(self, model=None):
        self.model = model
        self.filter = MagicMock()


@pytest.fixture
def mock_manager():
    """Fixture to create a test double of BaseManager."""
    return MockBaseManager()


def test_get_by_id_valid_int(mock_manager):
    """Test get_by_id with a valid integer ID."""
    mock_instance = MagicMock()
    mock_manager.filter.return_value.first.return_value = mock_instance

    result = mock_manager.get_by_id(1)

    assert result == mock_instance
    mock_manager.filter.assert_called_once_with(id=1)


def test_get_by_id_valid_str(mock_manager):
    """Test get_by_id with a valid string ID."""
    mock_instance = MagicMock()
    mock_manager.filter.return_value.first.return_value = mock_instance

    result = mock_manager.get_by_id("123")

    assert result == mock_instance
    mock_manager.filter.assert_called_once_with(id="123")


def test_get_by_id_invalid_id(mock_manager):
    """Test get_by_id with an invalid ID (non-numeric string)."""
    result = mock_manager.get_by_id("abc")

    assert result is None
    mock_manager.filter.assert_not_called()


def test_get_by_id_exception(mock_manager):
    """Test get_by_id when an exception occurs."""
    mock_manager.filter.side_effect = Exception("Database error")

    result = mock_manager.get_by_id(1)

    assert result is None
