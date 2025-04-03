# External
import re
from unittest.mock import patch, MagicMock, call

from django.db import IntegrityError, DatabaseError

# Internal
from ..base_test import TestClassBase
from ..base_model import BaseModel


class TestManagerGetByID(TestClassBase):
    """Unit tests for BaseManager get_by_id method behavior."""

    def setUp(self):
        """Runs before each test: Extends UnitTestBase setup."""

        super().setUp()


    def test_get_by_id_valid_int(self) -> None:
        """Test get_by_id with a valid integer ID."""

        # Mock filter().first() behavior
        with patch.object(self.base_manager, 'filter') as mock_filter:
            mock_filter.return_value.first.return_value = self.mock_service

            # Act: Call get_by_id with a valid integer ID
            result = self.base_manager.get_by_id(1)

            # Assert: Verify the result and method calls
            self.assertEqual(result, self.mock_service)
            mock_filter.assert_called_once_with(id=1)


    def test_get_by_id_negative_int(self) -> None:
        """Test get_by_id with a negative integer ID."""

        # Act
        result = self.base_manager.get_by_id(-1)

        # Assert
        self.assertIsNone(result)


    def test_get_by_id_valid_str(self) -> None:
        """Test get_by_id with a valid string ID."""

        # Mock filter().first() behavior
        with patch.object(self.base_manager, 'filter') as mock_filter:
            mock_filter.return_value.first.return_value = self.mock_service

            # Act
            result = self.base_manager.get_by_id("1")

            # Assert
            self.assertEqual(result, self.mock_service)
            mock_filter.assert_called_once_with(id="1")


    def test_get_by_id_with_invalid_str(self) -> None:
        """Test get_by_id with an invalid ID (non-numeric string)."""

        # Act
        result = self.base_manager.get_by_id("abc")

        # Assert
        self.assertIsNone(result)


    def test_get_by_id_zero(self) -> None:
        """Test get_by_id with a zero ID."""

        # Mock filter().first() behavior
        with patch.object(self.base_manager, 'filter') as mock_filter:
            mock_filter.return_value.first.return_value = self.mock_service

            # Act
            result = self.base_manager.get_by_id(0)

            # Assert
            self.assertEqual(result, self.mock_service)
            mock_filter.assert_called_once_with(id=0)


    def test_get_by_id_empty_str(self) -> None:
        """Test get_by_id with an empty string ID."""

        # Act
        result = self.base_manager.get_by_id("")

        # Assert
        self.assertIsNone(result)


    def test_get_by_id_none(self) -> None:
        """Test get_by_id with None as ID."""

        # Act
        result = self.base_manager.get_by_id(None)

        # Assert
        self.assertIsNone(result)


    def test_get_by_id_boolean_input(self) -> None:
        """Test get_by_id with boolean input."""

        # Act
        result = self.base_manager.get_by_id(False)

        # Assert
        self.assertIsNone(result)


    def test_get_by_id_exception(self) -> None:
        """Test get_by_id when an exception is raised."""

        # Arrange
        with patch.object(self.base_manager, 'filter') as mock_filter:
            mock_filter.side_effect = Exception("Database error")

            # Act
            with self.assertRaises(ValueError) as context:
                self.base_manager.get_by_id(123)

            # Assert
            self.assertEqual(str(context.exception), "Database error")
            mock_filter.assert_called_once_with(id=123)


    def test_get_by_id_large_int(self) -> None:
        """Test get_by_id with a large integer ID."""

        # Mock filter().first() behavior
        with patch.object(self.base_manager, 'filter') as mock_filter:
            mock_filter.return_value.first.return_value = self.mock_service

            # Act
            result = self.base_manager.get_by_id(999999999999999999)

            # Assert
            self.assertEqual(result, self.mock_service)
            mock_filter.assert_called_once_with(id=999999999999999999)


class TestManagerCreateInstance(TestClassBase):
    """Unit tests for BaseManager create_instance method behavior."""


    def setUp(self):
        """Runs before each test: Extends UnitTestBase setup."""

        super().setUp()
        self.mock_model.__name__ = "TestModel"


    def test_create_instance_success(self) -> None:
        """Test successful instance creation."""

        # Arrange
        self.base_manager.model = MagicMock(return_value=self.mock_service)
        self.mock_service.save.return_value = None  # Simulate save

        # Act
        instance = self.base_manager.create_instance(name="abc")

        # Assert
        self.assertIsNotNone(instance, "Expected an instance to be created")
        self.assertIs(instance, self.mock_service)
        self.base_manager.model.assert_called_once_with(name="abc")
        self.mock_service.save.assert_called_once()


    def test_create_instance_invalid_model(self) -> None:
        """Test create_instance when manager has no model attached."""

        # Arrange
        self.base_manager.model = None

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.base_manager.create_instance(name="Test Instance")

        self.assertEqual(
            str(context.exception),
            "BaseManager must be attached to a model before creating instances"
        )

        self.assert_no_errors_logged()
        self.assert_no_exceptions_logged()


    def test_create_instance_empty_kwargs(self) -> None:
        """Test create_instance with empty keyword arguments."""

        # Act
        result = self.base_manager.create_instance()

        # Assert
        self.assertIsNone(result)


    def test_create_instance_none_kwargs(self) -> None:
        """Test create_instance with None as keyword arguments."""

        # Act
        result = self.base_manager.create_instance(**{})

        # Assert
        self.assertIsNone(result)


    def test_create_instance_integrity_error(self) -> None:
        """Should log and return None on IntegrityError."""

        # Arrange
        self.mock_service.save.side_effect = IntegrityError("Duplicate entry")

        # Act
        result = self.base_manager.create_instance(name="Test Instance")

        # Assert
        self.assertIsNone(result)
        self.assert_logs_error(
            re.compile(r"IntegrityError in \w+: Duplicate entry")
        )


    def test_create_instance_database_error(self) -> None:
        """Should log and return None on DatabaseError."""

        # Arrange
        self.mock_service.save.side_effect = DatabaseError("Connection issue")

        # Act
        result = self.base_manager.create_instance(name="Test Instance")

        # Assert
        self.assertIsNone(result)
        self.assert_logs_error(
            re.compile(r"DatabaseError in \w+: Connection issue")
        )


    def test_create_instance_generic_exception(self) -> None:
        """Should log and return None on unexpected Exception."""

        # Arrange
        self.mock_service.save.side_effect = Exception("Unknown error")

        # Act
        result = self.base_manager.create_instance(name="Test Instance")

        # Assert
        self.assertIsNone(result)
        self.assert_logs_exception(
            re.compile(r"Unexpected error in \w+: Unknown error")
        )


class TestManagerLogError(TestClassBase):
    """Unit tests for the _log_error helper method."""

    def setUp(self):
        """Runs before each test: Extends UnitTestBase setup."""

        super().setUp()
        self.mock_model.__class__.__name__ = "TestModel"


    def test_log_error_with_instance_and_exception(self):
        """Test _log_error with instance provided and is_exception=True."""

        # Act
        self.base_manager._log_error(
            "IntegrityError", self.mock_model, Exception("Duplicate entry"),is_exception=True
        )

        # Assert
        expected_log_message = "IntegrityError in TestModel: Duplicate entry"
        self.mock_exception_logger.assert_called_once_with(
            expected_log_message,
            extra={"model": "TestModel", "error_type": "IntegrityError", "instance_id": self.mock_model.pk}
        )

    def test_log_error_with_instance_and_error(self):
        """Test _log_error with instance provided and is_exception=False."""

        # Act
        self.base_manager._log_error(
            "DatabaseError", self.mock_model, Exception("Connection error"), is_exception=False
        )

        # Assert
        expected_log_message = "DatabaseError in TestModel: Connection error"
        self.mock_error_logger.assert_called_once_with(
            expected_log_message,
            extra={"model": "TestModel", "error_type": "DatabaseError", "instance_id": self.mock_model.pk}
        )


    def test_log_error_without_instance(self):
        """Test _log_error without instance (fallback to self.model)."""

        # Act
        self.base_manager._log_error(
            "Unexpected error", None, Exception("Unknown error"), is_exception=False
        )

        # Assert
        expected_log_message = "Unexpected error in unknown_model: Unknown error"
        self.mock_error_logger.assert_called_once_with(
            expected_log_message,
            extra={"model": "unknown_model", "error_type": "Unexpected error"}
        )

    def test_log_error_without_instance_and_model_name(self):
        """Test _log_error without instance and without self.model.__name__ (fallback to 'unknown model')."""

        # Arrange: Remove __name__ from self.model
        delattr(self.base_manager.model, "__name__")

        # Act
        self.base_manager._log_error(
            "Unexpected error", None, Exception("Unknown error"), is_exception=False
        )

        # Assert
        expected_log_message = "Unexpected error in unknown_model: Unknown error"
        self.mock_error_logger.assert_called_once_with(
            expected_log_message,
            extra={"model": "unknown_model", "error_type": "Unexpected error"}
        )


class TestManagerBulk(TestClassBase):
    """Unit tests for BaseManager bulk_create_instances, bulk_update_instances, bulk_delete_instances methods behavior."""

    def setUp(self):
        """Runs before each test: Extends UnitTestBase setup."""

        super().setUp()
        self.mock_model.__name__ = "TestModel"
        self.test_fields = ['field1', 'field2']
        self.test_objects = [MagicMock(spec=BaseModel) for _ in range(5)]


    def test_bulk_create_instances_success(self) -> None:
        """Test successful bulk creation of instances."""

        # Arrange
        self.base_manager.bulk_create = MagicMock(return_value=self.test_objects)

        # Act
        result = self.base_manager.bulk_create_instances(self.test_objects, batch_size=2)

        # Assert
        self.assertEqual(result, self.test_objects)
        self.base_manager.bulk_create.assert_called_once_with(self.test_objects, batch_size=2)
        self.assert_no_errors_logged()
        self.assert_no_exceptions_logged()


    def test_bulk_create_instances_empty_list(self) -> None:
        """Test bulk creation with empty objects list."""

        # Act
        result = self.base_manager.bulk_create_instances([])

        # Assert
        self.assertEqual(result, [])
        self.assert_no_errors_logged()
        self.assert_no_exceptions_logged()


    def test_bulk_create_instances_integrity_error(self) -> None:
        """Test bulk creation handling of IntegrityError."""

        # Arrange
        integrity_error = IntegrityError("Duplicate entry")
        self.base_manager.bulk_create = MagicMock(side_effect=integrity_error)

        # Act
        result = self.base_manager.bulk_create_instances(self.test_objects)

        # Assert
        self.assertEqual(result, [])
        self.assert_logs_error(re.compile(r"IntegrityError during bulk_create TestModel"))
        self.assert_no_exceptions_logged()


    def test_bulk_create_instances_unexpected_error(self) -> None:
        """Test bulk creation handling of unexpected errors."""

        # Arrange
        unexpected_error = Exception("Database connection failed")
        self.base_manager.bulk_create = MagicMock(side_effect=unexpected_error)

        # Act & Assert
        with self.assertRaises(Exception) as context:
            self.base_manager.bulk_create_instances(self.test_objects)

        self.assertEqual(str(context.exception), "Database connection failed")
        self.assert_logs_exception(
            re.compile(r"Unexpected error during bulk_create TestModel")
        )


    def test_bulk_update_instances_success(self) -> None:
        """Test successful bulk update of instances."""

        # Arrange
        self.base_manager.bulk_update = MagicMock()

        # Act
        result = self.base_manager.bulk_update_instances(self.test_objects, self.test_fields, batch_size=2)

        # Assert
        self.assertEqual(result, self.test_objects)
        # Should make 3 calls (5 items with batch_size=2)
        self.assertEqual(self.base_manager.bulk_update.call_count, 3)
        self.assert_no_errors_logged()
        self.assert_no_exceptions_logged()


    def test_bulk_update_instances_integrity_error(self) -> None:
        """Test bulk update handling of IntegrityError."""

        # Arrange
        integrity_error = IntegrityError("Duplicate entry")
        self.base_manager.bulk_update = MagicMock(side_effect=integrity_error)  # type: ignore[method-assign]

        # Act
        result = self.base_manager.bulk_update_instances(self.test_objects, self.test_fields)

        # Assert
        self.assertEqual(result, [])
        self.assert_logs_error(re.compile(r"IntegrityError during bulk_create TestModel"))
        self.assert_no_exceptions_logged()


    def test_bulk_update_instances_unexpected_error(self) -> None:
        """Test bulk update handling of unexpected errors."""

        # Arrange
        unexpected_error = Exception("Database connection failed")
        self.base_manager.bulk_update = MagicMock(side_effect=unexpected_error)

        # Act & Assert
        with self.assertRaises(Exception) as context:
            self.base_manager.bulk_update_instances(self.test_objects, self.test_fields)

        self.assertEqual(str(context.exception), "Database connection failed")
        self.assert_logs_exception(
            re.compile(r"Unexpected error during bulk_create TestModel")
        )


    def test_bulk_update_instances_empty_objects(self) -> None:
        """Test bulk update with empty objects list."""

        # Act
        result = self.base_manager.bulk_update_instances([], self.test_fields)

        # Assert
        self.assertEqual(result, [])
        self.assert_no_errors_logged()
        self.assert_no_exceptions_logged()


    def test_bulk_update_instances_empty_fields(self) -> None:
        """Test bulk update with empty fields list."""

        # Arrange & Act
        result = self.base_manager.bulk_update_instances(self.test_objects, [])

        # Assert
        self.assertEqual(result, [])
        self.assert_no_errors_logged()
        self.assert_no_exceptions_logged()


    def test_bulk_update_instances_batch_processing(self) -> None:
        """Test that bulk update properly batches objects."""

        # Arrange
        test_objects = [MagicMock(spec=BaseModel) for _ in range(10)]
        self.base_manager.bulk_update = MagicMock()

        # Act
        self.base_manager.bulk_update_instances(test_objects, self.test_fields, batch_size=3)

        # Assert
        # Should make 4 calls (10 items with batch_size=3)
        self.assertEqual(self.base_manager.bulk_update.call_count, 4)

        # Verify batches are correct
        batches = [call.args[0] for call in self.base_manager.bulk_update.call_args_list]
        self.assertEqual(len(batches[0]), 3)  # First 3 batches have 3 items
        self.assertEqual(len(batches[3]), 1)  # Last batch has 1 item


    def test_bulk_delete_instances_success(self) -> None:
        """Test successful bulk deletion with filters."""

        # Arrange
        test_objects = [MagicMock(spec=BaseModel) for _ in range(3)]
        for i, instance in enumerate(test_objects, 1):
            instance.pk = i

        # Create two separate mock querysets
        find_queryset = MagicMock()
        find_queryset.__iter__.return_value = iter(test_objects)

        delete_queryset = MagicMock()

        # Configure filter_by to return different querysets
        self.base_manager.filter_by = MagicMock(side_effect=[
            find_queryset,  # First call returns instances
            delete_queryset  # Second call returns delete queryset
        ])

        # Act & Assert
        result = self.base_manager.bulk_delete_instances(status="inactive")
        self.assertEqual(result, test_objects)

        # Verify filter_by calls using call()
        calls = self.base_manager.filter_by.call_args_list
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0], call(status="inactive"))
        self.assertEqual(calls[1], call(pk__in=[1, 2, 3]))

        delete_queryset.delete.assert_called_once()
        self.assert_no_errors_logged()
        self.assert_no_exceptions_logged()


    def test_bulk_delete_instances_integrity_error(self) -> None:
        """Test bulk delete handling of IntegrityError."""

        # Arrange
        mock_instances = [MagicMock(spec=BaseModel)]
        mock_instances[0].pk = 1

        # Set up mock queryset that will raise IntegrityError
        self.mock_service.filter_by.return_value = self.mock_service
        self.mock_service.__iter__.return_value = iter(mock_instances)
        self.mock_service.delete.side_effect = IntegrityError("Foreign key constraint")
        self.base_manager.filter_by = MagicMock(return_value=self.mock_service)
        # Clear any previous mock calls
        self.mock_error_logger.reset_mock()

        # Act
        result = self.base_manager.bulk_delete_instances(status="old")

        # Assert
        self.assertEqual(result, [])

        logged_message = None
        for call_arg in self.mock_error_logger.call_args_list:
            if "IntegrityError during bulk_delete TestModel" in call_arg[0][0]:
                logged_message = call_arg[0][0]
                break

        self.assertIsNotNone(logged_message, "Expected error log not found")
        self.assertIn("Foreign key constraint", logged_message)
        self.assert_no_exceptions_logged()


    def test_bulk_delete_instances_unexpected_error(self) -> None:
        """Test bulk delete handling of unexpected errors."""
        # Arrange
        self.mock_model.pk = 1

        # Set up mock queryset that will raise unexpected error during iteration
        self.mock_service.filter_by.return_value = self.mock_service
        self.mock_service.__iter__.side_effect = Exception("Database connection failed")
        self.base_manager.filter_by = MagicMock(return_value=self.mock_service)
        # Clear previous mock calls
        self.mock_exception_logger.reset_mock()

        # Act & Assert
        with self.assertRaises(Exception) as context:
            self.base_manager.bulk_delete_instances(category="test")

        self.assertEqual(str(context.exception), "Database connection failed")

        self.assert_logs_exception(
            re.compile(r"Unexpected error during bulk_delete TestModel")
        )

        self.assertIn("Database connection failed", str(context.exception))


    def test_bulk_delete_instances_empty_filters(self) -> None:
        """Test bulk delete with empty fil dict."""

        # Arrange
        self.base_manager.filter_by = self.mock_service

        # Act
        result = self.base_manager.bulk_delete_instances()

        # Assert
        self.assertEqual(result, [])
        self.base_manager.filter_by.assert_not_called()
        self.assert_no_errors_logged()
        self.assert_no_exceptions_logged()


    def test_bulk_delete_instances_no_matches(self) -> None:
        """Test bulk delete when no instances match filters."""

        # Arrange
        self.mock_service.filter_by.return_value = self.mock_service
        self.mock_service.__iter__.return_value = iter([])
        self.base_manager.filter_by = self.mock_service

        # Act
        result = self.base_manager.bulk_delete_instances(active=False)

        # Assert
        self.assertEqual(result, [])
        self.base_manager.filter_by.assert_called_once_with(active=False)
        self.mock_service.delete.assert_not_called()
        self.assert_no_errors_logged()


class TestBaseModel(TestClassBase):
    """Unit tests for BaseModel behavior."""


    def setUp(self):
        """Runs before each test: Extends UnitTestBase setup."""

        super().setUp()
        self.test_model.pk = 1


    def test_commit_success(self) -> None:
        """Test successful transaction commit."""

        # Act
        self.test_model.commit()

        # Assert
        self.mock_commit.assert_called_once()
        self.mock_rollback.assert_not_called()
        self.assert_no_errors_logged()


    def test_commit_failure(self) -> None:
        """Test transaction commit failure with rollback."""

        # Arrange
        self.mock_commit.side_effect = Exception("Database error")

        # Act
        with self.assertRaises(Exception) as ctx:
            self.test_model.commit()

        # Assert
        self.assertEqual(str(ctx.exception), "Database error")
        self.mock_rollback.assert_called_once()
        self.assert_logs_exception("Transaction commit failed: Database error")


    def test_before_update_success(self) -> None:
        """Test successful execution of before_update hook."""

        # Act
        self.test_model.before_update()

        # Assert
        self.assert_logs_info(f"Running before_update hook for {self.test_model.__class__.__name__}.")
        self.assert_no_errors_logged()
        self.assert_no_exceptions_logged()


    def test_before_update_failure(self) -> None:
        """Test before_update hook with an unexpected error."""

        # Arrange
        self.mock_service.side_effect = RuntimeError("Unexpected error")
        self.test_model._before_update_hook = self.mock_service

        # Act
        with self.assertRaises(RuntimeError):
            self.test_model.before_update()

        # Assert
        self.assert_logs_exception(
            f"Unexpected error in before_update for {self.test_model.__class__.__name__}: Unexpected error"
        )


    def test_after_update_success(self) -> None:
        """Test successful execution of after_update hook."""

        # Act
        self.test_model.after_update()

        # Assert
        self.assert_logs_info(f"Running after_update hook for {self.test_model.__class__.__name__}.")
        self.assert_no_errors_logged()
        self.assert_no_exceptions_logged()


    def test_after_update_failure(self) -> None:
        """Test after_update hook with an unexpected error."""

        # Arrange
        self.mock_service.side_effect = RuntimeError("Unexpected error")
        self.test_model._after_update_hook = self.mock_service

        # Act
        with self.assertRaises(RuntimeError):
            self.test_model.after_update()

        # Assert
        self.assert_logs_exception(
            f"Unexpected error in after_update for {self.test_model.__class__.__name__}: Unexpected error"
        )


    def test_update_success(self) -> None:
        """Test that update works correctly when no errors occur."""

        # Arrange
        with patch.object(self.test_model, "before_update") as mock_before_update, \
                patch.object(self.test_model, "after_update") as mock_after_update, \
                patch.object(self.test_model, "save") as mock_save:

            # Act
            self.test_model.update(name="New Name", description="Updated Description")

            # Assert hooks
            mock_before_update.assert_called_once()
            mock_save.assert_called_once_with()
            mock_after_update.assert_called_once()
            # Assert update logs a success message
            expected_info = f"Updated {self.test_model.__class__.__name__} (ID: {self.test_model.pk}) successfully"
            self.assert_logs_info(expected_info)


    def test_update_failure(self) -> None:
        """Test that update() logs an exception and re-raises when before_update fails via lambda."""

        # Arrange
        self.test_model.before_update = lambda: (_ for _ in ()).throw(Exception("Hook failure"))

        # Act
        with self.assertRaises(Exception) as ctx:
            self.test_model.update(name="New Name", description="Should fail")

        # Assert
        self.assertIn("Hook failure", str(ctx.exception))
        expected_error = f"Error updating {self.test_model.__class__.__name__}: Hook failure"
        self.assert_logs_exception(expected_error)


    def test_update_handles_unexpected_exception(self) -> None:
        """Ensure update logs an exception and raises it if something unexpected occurs."""

        # Arrange
        with patch.object(BaseModel, "save", side_effect=Exception("Unexpected DB error")):
            with self.assertRaises(Exception) as ctx:

                # Act
                self.test_model.update(name="New Name", description="Updated Description")

            # Assert
            self.assertIn("Unexpected DB error", str(ctx.exception))
            expected_error = f"Error updating {self.test_model.__class__.__name__}: Unexpected DB error"
            self.assert_logs_exception(expected_error)


    def test_before_save_success(self) -> None:
        """Ensure `before_save` logs the correct message."""

        # Act
        self.test_model.before_save()

        # Assert
        self.assert_logs_info(f"Running before_save hook for {self.test_model.__class__.__name__}.")
        self.assert_no_errors_logged()
        self.assert_no_exceptions_logged()


    def test_before_save_failure(self) -> None:
        """Ensure `before_save` logs an exception if an error occurs."""

        # Arrange
        self.mock_service.side_effect = RuntimeError("Unexpected error")
        self.test_model._before_save_hook = self.mock_service

        # Act
        with self.assertRaises(RuntimeError):
            self.test_model.before_save()

        # Assert
        self.assert_logs_exception(
            f"Unexpected error in before_save for {self.test_model.__class__.__name__}: Unexpected error"
        )


    def test_after_save_success(self) -> None:
        """Ensure `after_save` logs the correct message."""

        # Act
        self.test_model.after_save()

        # Assert
        self.assert_logs_info(f"Running after_save hook for {self.test_model.__class__.__name__}.")
        self.assert_no_errors_logged()
        self.assert_no_exceptions_logged()


    def test_after_save_failure(self) -> None:
        """Ensure `before_save` logs an exception if an error occurs."""

        # Arrange
        self.mock_service.side_effect = RuntimeError("Unexpected error")
        self.test_model._after_save_hook = self.mock_service

        # Act
        with self.assertRaises(RuntimeError):
            self.test_model.after_save()

        # Assert
        self.assert_logs_exception(
            f"Unexpected error in after_save for {self.test_model.__class__.__name__}: Unexpected error"
        )


    def test_save_success(self) -> None:
        """Test that save() works correctly when no errors occur."""

        # Arrange
        with patch("django.db.models.Model.save", autospec=True) as mock_parent_save:

            # Act
            self.test_model.save()

            # Assert
            mock_parent_save.assert_called_once_with(self.test_model)
            expected_info = f"Successfully saved {self.test_model.__class__.__name__} (ID: {self.test_model.pk})"
            self.assert_logs_info(expected_info)


    def test_save_failure_due_to_before_save_failure(self) -> None:
        """Test that save() logs an exception and re-raises when before_save fails via lambda."""

        # Arrange: Override before_save with a lambda that raises an exception.
        self.test_model.before_save = lambda: (_ for _ in ()).throw(Exception("Unexpected error in before_save"))
        self.test_model.after_save = lambda: None

        # Act
        with self.assertRaises(Exception) as ctx:
            self.test_model.save(commit=True)

        # Assert
        self.assertIn("Unexpected error in before_save", str(ctx.exception))
        self.assert_logs_exception(
            re.compile(r"Unexpected error in \w+\.save\(\): Unexpected error in before_save")
        )


    def test_save_handles_integrity_error(self) -> None:
        """Ensure that save() handles IntegrityError and logs it."""

        # Arrange: Override hooks with no-ops
        self.test_model.before_save = lambda: None
        self.test_model.after_save = lambda: None

        with patch("django.db.models.Model.save", autospec=True,
                   side_effect=IntegrityError("Integrity issue")) as mock_parent_save:
            # Act
            with self.assertRaises(IntegrityError) as exc_context:
                self.test_model.save()

            # Assert: Exception content
            self.assertIn("Integrity issue", str(exc_context.exception))

            # Assert: save and transaction.atomic were called
            mock_parent_save.assert_called_once_with(self.test_model)
            self.assert_logs_error(
                re.compile(rf"IntegrityError in {self.test_model.__class__.__name__}\.save\(\): Integrity issue")
            )


    def test_save_handles_unexpected_exception(self) -> None:
        """Ensure that save() logs unexpected exceptions and re-raises them."""

        # Arrange
        self.test_model.before_save = lambda: None
        self.test_model.after_save = lambda: None

        with patch("django.db.models.Model.save", autospec=True,
                   side_effect=Exception("Unexpected error")) as mock_parent_save:
            # Act
            with self.assertRaises(Exception) as ctx:
                self.test_model.save(commit=True)

            self.assertIn("Unexpected error", str(ctx.exception))
            mock_parent_save.assert_called_once_with(self.test_model)
            self.assert_logs_exception(
                re.compile(r"Unexpected error in \w+\.save\(\): Unexpected error")
            )


    def test_delete_success(self) -> None:
        """Ensure `delete` logs a success message when an instance is deleted."""

        # Arrange
        with patch("django.db.models.Model.delete", autospec=True) as mock_parent_delete:

            # Act
            self.test_model.delete()

            # Assert
            mock_parent_delete.assert_called_once_with(self.test_model)
            self.assert_logs_info(
                f"Deleted {self.test_model.__class__.__name__} (ID: {self.test_model.pk}) successfully"
            )


    def test_delete_handles_exception(self) -> None:
        """Ensure `delete` logs and raises exceptions correctly."""

        # Arrange
        with patch("django.db.models.Model.delete", autospec=True,
                   side_effect=Exception("Deletion failed")) as mock_parent_delete:
            # Act
            with self.assertRaises(Exception) as ctx:
                self.test_model.delete()

            # Assert
            self.assertIn("Deletion failed", str(ctx.exception))
            mock_parent_delete.assert_called_once_with(self.test_model)
            self.assert_logs_exception(
                f"Error deleting {self.test_model.__class__.__name__} (ID: {self.test_model.pk}): Deletion failed"
            )
