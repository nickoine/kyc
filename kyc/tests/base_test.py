from __future__ import annotations

# External
from django.test import SimpleTestCase
from django.db import models

# Internal
from unittest.mock import MagicMock, patch
from ..common import DBManager, BaseModel


class ModelTest(BaseModel):
    """Concrete model for testing."""

    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        app_label = "test"


class TestClassBase(SimpleTestCase):
    """Base class for unit tests, ensuring consistent setup and isolation."""


    def setUp(self) -> None:
        """Common setup for unit tests: patch dependencies, mock services, and configure logging."""

        super().setUp()

        # Mock external services
        self.mock_service = MagicMock()

        # Mock database models
        self.real_mock_model = ModelTest(name="ModelTest")
        self.mock_model = MagicMock(spec=ModelTest)
        self.mock_model.return_value = self.mock_service

        # Mock db manager
        self.real_mock_manager = DBManager()
        self.mock_manager = MagicMock(spec=DBManager)
        self.mock_manager.model = self.mock_model # type: ignore[assignment]

        # Mock the transaction module
        self.mock_commit = patch("django.db.transaction.commit").start()
        self.mock_rollback = patch("django.db.transaction.rollback").start()

        # Mock logger
        self.mock_logger = patch("kyc.common.base_model.logger").start()
        self.mock_info_logger = self.mock_logger.info
        self.mock_error_logger = self.mock_logger.error
        self.mock_exception_logger = self.mock_logger.exception

        self.mock_cache = patch("django.core.cache.cache").start()

        # Mock environment variables (optional, uncomment if needed)
        # self.mock_env = patch.dict(os.environ, {"CONFIG_VAR": "mocked"}).start()

        # Mock Django signals (optional, uncomment if needed)
        # self.mock_signal = patch("path.models.signals.post_save.send").start()

        # Mock UUID generation (optional, uncomment if needed)
        # self.mock_uuid = patch("uuid.uuid4", return_value=uuid.UUID("12345678-1234-5678-1234-567812345678")).start()

        # Mock threading (optional, uncomment if needed)
        # self.mock_thread = patch("threading.Thread.start").start()

        # Mock async functions (optional, uncomment if needed)
        # self.mock_async_function = patch("path.tasks.some_async_function", new_callable=AsyncMock).start()

        # Freeze time for consistent timestamps (optional, uncomment if needed)
        # self.frozen_time = freezegun.freeze_time("2025-01-01")
        # self.frozen_time.start()


    def tearDown(self) -> None:
        """Stops all patches and unfreezes time after each test."""

        patch.stopall()  # Stop all active patches

        # Unfreeze time if frozen_time is used (optional, uncomment if needed)
        if hasattr(self, "frozen_time"):
            self.frozen_time.stop()

        super().tearDown()


    def assert_logs_error(self, expected_message: str) -> None:
        """Helper to verify if a specific error log was triggered."""
        self.mock_error_logger.assert_called_with(expected_message)


    def assert_no_errors_logged(self) -> None:
        """Helper to verify no errors are logged."""
        self.mock_error_logger.assert_not_called()


    def assert_logs_info(self, expected_message: str) -> None:
        """Helper to verify if an info log was triggered."""
        self.mock_info_logger.assert_called_with(expected_message)


    def assert_no_infos_logged(self) -> None:
        """Helper to verify if an info log was triggered."""
        self.mock_info_logger.assert_not_called()


    def assert_logs_exception(self, expected_message: str) -> None:
        """Helper to verify if a specific exception was triggered."""
        self.mock_exception_logger.assert_called_with(expected_message)


    def assert_no_exceptions_logged(self) -> None:
        """Helper to verify if a specific exception was triggered."""
        self.mock_exception_logger.assert_not_called()
