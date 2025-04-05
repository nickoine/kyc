import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kyc.etc.dev")
django.setup()


# import pytest
# from unittest.mock import MagicMock, patch
# from common.base_model import BaseManager
#
# # ----------------------------------------
# # 🔹 FUNCTION-SCOPED FIXTURES (Default)
# # These reset before every test function
# # ----------------------------------------
#
# @pytest.fixture
# def mock_manager() -> MagicMock:
#     """Fixture to create a test double of BaseManager for individual tests."""
#     mock_manager = MagicMock(spec=BaseManager)
#     mock_manager.filter.return_value.first.return_value = MagicMock()
#     return mock_manager
#
# @pytest.fixture
# def mock_logger() -> MagicMock:
#     """Fixture providing a fresh mock logger for each test function."""
#     return MagicMock()
#
# @pytest.fixture
# def mock_get_by_id():
#     """Fixture to patch BaseManager.get_by_id method for individual tests."""
#     with patch("path.to.BaseManager.get_by_id") as mock_method:
#         yield mock_method
#
# # ----------------------------------------
# # 🔹 CLASS-SCOPED FIXTURES
# # These reset once per test class
# # ----------------------------------------
#
# @pytest.fixture(scope="class")
# def class_mock_manager() -> MagicMock:
#     """Provides a class-scoped mock manager, reset per test class."""
#     return MagicMock()
#
# @pytest.fixture(scope="class")
# def class_mock_logger() -> MagicMock:
#     """Provides a class-scoped mock logger, reset per test class."""
#     return MagicMock()
#
# # ----------------------------------------
# # 🔹 SESSION-SCOPED FIXTURES
# # These persist across all tests
# # ----------------------------------------
#
# @pytest.fixture(scope="session")
# def session_mock_manager() -> MagicMock:
#     """Provides a session-scoped mock manager shared across all tests."""
#     return MagicMock()
