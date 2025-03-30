# External
from __future__ import annotations
from django.db import transaction, IntegrityError, DatabaseError
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Model, Manager
from django.db import models

# Internal
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

from typing import TYPE_CHECKING, Any, Dict, TypeVar, Type
if TYPE_CHECKING:
    from django.db.models import QuerySet
    from typing import Optional, List


T = TypeVar("T", bound="Model")

class AbstractManager(ABC):
    """Abstract manager for common query operations."""

    @abstractmethod
    def get_by_id(self, obj_id: int | str) -> object | None:
        return self


    @abstractmethod
    def create_instance(self, **kwargs) -> object | None:
        return self


class BaseManager(AbstractManager, Manager[T]):
    """Manager for common query operations."""

    model: Type[T]

    def get_by_id(self, obj_id: int | str) -> QuerySet | None:
        """Fetch an instance by ID if it's valid."""

        if not isinstance(obj_id, (int, str)) or not str(obj_id).isdigit():
            return None

        try:
            return self.filter(id=obj_id).first()

        except ObjectDoesNotExist:
            return None
        except Exception as e:
            self._log_error("Unexpected error during fetching", None, e, is_exception=True)
            raise ValueError(str(e)) from e


    def get_all(self) -> QuerySet:
        """Return all objects of the model."""
        return self.all()


    def filter_by(self, **filters) -> QuerySet:
        """Return objects that match the given filters."""
        return self.filter(**filters)


    def exists(self, **filters) -> bool:
        """Check if an object with given filters exists."""
        return self.filter(**filters).exists()


    def create_instance(self, **kwargs) -> Optional[Model | None]:
        """Create and return an instance."""

        if not kwargs:
            return None
        if not getattr(self, "model", None):
            raise ValueError("BaseManager must be attached to a model before creating instances")
        instance = None

        try:
            instance = self.model(**kwargs)
            instance.save()
            return instance

        except IntegrityError as e:
            self._log_error("IntegrityError", instance, e)
        except DatabaseError as e:
            self._log_error("DatabaseError", instance, e)
        except Exception as e:
            self._log_error("Unexpected error", instance, e, is_exception=True)

        return None


    def bulk_create_instances(self, objects: List[Model], batch_size: int = 100) -> List[Model]:
        """Bulk create instances and return the created objects."""

        if not objects:
            return []

        model_name = self.model.__name__

        try:
            created_instances = self.bulk_create(objects, batch_size=batch_size)
            return created_instances

        except IntegrityError as e:
            self._log_error(f"IntegrityError during bulk_create {model_name}", None, e)

        except Exception as e:
            self._log_error(
                f"Unexpected error during bulk_create {model_name}", None, e, is_exception=True
            )
            raise
        return []


    def bulk_update_instances(self, objects: List[Model], fields: List[str], *, batch_size: int = 100) -> List[Model]:
        """Atomically bulk update instances in batches."""

        if not objects or not fields:
            return []

        model_name = self.model.__name__

        try:
            for i in range(0, len(objects), batch_size):
                batch = objects[i:i + batch_size]
                self.bulk_update(batch, fields=fields)
            return objects

        except IntegrityError as e:
            self._log_error(f"IntegrityError during bulk_create {model_name}", None, e)

        except Exception as e:
            self._log_error(
                f"Unexpected error during bulk_create {model_name}", None, e, is_exception=True
            )
            raise
        return []


    def bulk_delete_instances(self, **filters) -> List[Model]:
        """Bulk delete instances matching filters atomically."""

        if not filters:
            return []

        model_name = self.model.__name__

        try:
            instances = list(self.filter_by(**filters))
            if instances:
                self.filter_by(pk__in=[obj.pk for obj in instances]).delete()
            return instances

        except IntegrityError as e:
            self._log_error(f"IntegrityError during bulk_delete {model_name}", None, e)

        except Exception as e:
            self._log_error(
                f"Unexpected error during bulk_delete {model_name}", None, e, is_exception=True
            )
            raise
        return  []


    def _log_error(
            self,
            error_type: str,
            instance: Optional[BaseModel] = None,
            error: Optional[Exception] = None,
            *,
            is_exception: bool = False,
            is_information: bool = False,
            extra: Optional[Dict[str, Any]] = None,
            **kwargs: Any
    ) -> None:
        """Unified logging helper for repository operations with structured context."""

        model_name = "unknown_model"
        if instance is not None:
            model_name = instance.__class__.__name__
        elif hasattr(self, 'model') and hasattr(self.model, '__name__'):
            model_name = self.model.__name__

        log_data = {
            "model": model_name,
            "error_type": error_type,
            **kwargs
        }

        if extra:
            log_data.update(extra)

        if instance is not None and hasattr(instance, 'pk'):
            log_data['instance_id'] = instance.pk

        error_message = str(error) if error else "Unknown error"
        log_message = f"{error_type} in {model_name}: {error_message}"

        if is_exception:
            logger.exception(log_message, extra=log_data)
        elif is_information:
            logger.info(log_message, extra=log_data)
        else:
            logger.error(log_message, extra=log_data)


#
# class UserManager(BaseManager):
#     pass
#
#
# class AccountsManager(BaseManager):
#     pass
#
#
# class AdminsManager(BaseManager):
#     pass
#
#
# class RolesManager(BaseManager):
#     pass
#
#
# class UserResponsesManager(BaseManager):
#     pass


class BaseModel(Model):
    """Abstract base model with common CRUD methods."""

    id = models.AutoField(primary_key=True)
    objects = BaseManager()


    class Meta:
        abstract = True


    @classmethod
    def commit(cls) -> None:
        """Commit all pending changes in the database session."""

        try:
            transaction.commit()

        except Exception as e:
            transaction.rollback()
            logger.exception(f"Transaction commit failed: {e}")
            raise e


    def before_update(self) -> None:
        """Hook to run custom logic before updating."""

        try:
            logger.info(f"Running before_update hook for {self.__class__.__name__}.")
            self._before_update_hook()
        except Exception as e:
            logger.exception(f"Unexpected error in before_update for {self.__class__.__name__}: {e}")
            raise e


    def _before_update_hook(self) -> None:
        pass


    def after_update(self) -> None:
        """Hook to run custom logic after updating."""

        try:
            logger.info(f"Running after_update hook for {self.__class__.__name__}.")
            self._after_update_hook()
        except Exception as e:
            logger.exception(f"Unexpected error in after_update for {self.__class__.__name__}: {e}")
            raise e


    def _after_update_hook(self) -> None: # for test
        pass


    def update(self, **kwargs) -> None:
        """Update model fields and save the instance safely."""

        if kwargs is None or not kwargs:
            return None

        try:
            self.before_update()

            for attr, value in kwargs.items():
                setattr(self, attr, value)
            self.save()
            logger.info(f"Updated {self.__class__.__name__} (ID: {self.pk}) successfully")

            self.after_update()

        except Exception as e:
            logger.exception(f"Error updating {self.__class__.__name__}: {e}")
            raise


    def before_save(self) -> None:
        """Hook to run custom logic before saving."""

        try:
            logger.info(f"Running before_save hook for {self.__class__.__name__}.")
            self._before_save_hook()
        except Exception as e:
            logger.exception(f"Unexpected error in before_save for {self.__class__.__name__}: {e}")
            raise e


    def _before_save_hook(self) -> None:
        pass


    def after_save(self) -> None:
        """Hook to run custom logic after saving."""

        try:
            logger.info(f"Running after_save hook for {self.__class__.__name__}.")
            self._after_save_hook()
        except Exception as e:
            logger.exception(f"Unexpected error in after_save for {self.__class__.__name__}: {e}")
            raise e


    def _after_save_hook(self) -> None:
        pass


    def save(self, commit: bool = False, *args, **kwargs) -> None:
        """Save instance with transaction handling."""

        if args:
            raise ValueError("Unexpected positional arguments passed to save()")
        if not isinstance(commit, bool):
            raise ValueError("Commit must be a boolean")

        try:
            self.before_save()
            super().save(*args, **kwargs)
            logger.info(f"Successfully saved {self.__class__.__name__} (ID: {self.pk})")
            self.after_save()

        except IntegrityError as e:
            logger.error(f"IntegrityError in {self.__class__.__name__}.save(): {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error in {self.__class__.__name__}.save(): {e}")
            raise


    def delete(self, *args, **kwargs) -> None:
        """Delete instance with exception handling."""

        try:
            super().delete(*args, **kwargs)
            logger.info(f"Deleted {self.__class__.__name__} (ID: {self.pk}) successfully")

        except Exception as e:
            logger.exception(f"Error deleting {self.__class__.__name__} (ID: {self.pk}): {e}")
            raise
