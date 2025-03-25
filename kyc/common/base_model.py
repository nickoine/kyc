# External
from __future__ import annotations
from typing import Optional, List
from abc import ABC, abstractmethod

import logging
logger = logging.getLogger(__name__)

from django.db import models, transaction, IntegrityError, DatabaseError
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet


class AbstractManager(ABC):
    """Abstract manager for common query operations."""

    @abstractmethod
    def get_by_id(self, obj_id: int | str) -> object | None:
        return self


    @abstractmethod
    def create_instance(self, **kwargs) -> object | None:
        return self


class BaseManager(AbstractManager, models.Manager):
    """Manager for common query operations."""


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


    def create_instance(self, **kwargs) -> QuerySet | None:
        """Create and return an instance."""

        if kwargs is None or not kwargs:
            return None

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


    def bulk_create_instances(self, objects: List[models.Model], batch_size: int = 100) -> None:
        """Efficiently bulk create instances."""

        if not objects:
            return

        try:
            self.bulk_create(objects, batch_size=batch_size)

        except IntegrityError as e:
            self._log_error("IntegrityError during bulk_create", None, e)
        except Exception as e:
            self._log_error("Unexpected error during bulk_create", None, e, is_exception=True)


    def bulk_update_instances(self, objects: List[models.Model], fields: List[str], batch_size: int = 100) -> None:
        """Efficiently bulk update instances."""

        if not objects or not fields:
            return

        try:
            self.bulk_update(objects, fields, batch_size=batch_size)

        except IntegrityError as e:
            self._log_error("IntegrityError during bulk_update", None, e)
        except Exception as e:
            self._log_error("Unexpected error during bulk_update", None, e, is_exception=True)


    def bulk_delete_instances(self, **filters) -> int:
        """Delete multiple records matching the given filters."""

        try:
            deleted_count, _ = self.filter(**filters).delete()
            return deleted_count

        except Exception as e:
            self._log_error("Error in bulk_delete", None, e, is_exception=True)
            return 0


    def _log_error(self,
                   error_type: str,
                   instance: Optional[BaseModel],
                   error: Exception,
                   is_exception: bool = False) -> None:
        """Helper method to log errors."""

        model_name = instance.__class__.__name__ if\
            instance else self.model.__name__ if\
            hasattr( self.model, "__name__") else "unknown model"

        message = f"{error_type} while creating {model_name}: {error}"

        if is_exception:
            logger.exception(message)
        else:
            logger.error(message)


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
# class QuestionnairesManager(BaseManager):
#     pass
#
#
# class QuestionsManager(BaseManager):
#     pass
#
#
# class UserResponsesManager(BaseManager):
#     pass


class BaseModel(models.Model):
    """Abstract base model with common CRUD methods."""

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
            with transaction.atomic():
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
