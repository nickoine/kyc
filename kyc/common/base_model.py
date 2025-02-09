# External
from __future__ import annotations
from abc import ABC, abstractmethod
import logging

from django.db import models, transaction, IntegrityError, DatabaseError

logger = logging.getLogger(__name__)


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


    def get_by_id(self, obj_id: int | str) -> object | None:
        """Fetch an instance by ID if it's valid."""

        try:
            if isinstance(obj_id, (int, str)) and str(obj_id).isdigit():
                return self.filter(id=obj_id).first()

        except Exception as e:
            logger.error(f"Error fetching {self.model.__name__} by ID {obj_id}: {e}")
        return None


    def create_instance(self, **kwargs) -> object | None:
        """Create and return an instance."""

        try:
            instance = self.model(**kwargs)
            instance.save()
            return instance

        except IntegrityError as e:
            logger.error(f"IntegrityError while creating {self.model.__name__}: {e}")
        except DatabaseError as e:
            logger.error(f"DatabaseError while creating {self.model.__name__}: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error while creating {self.model.__name__}: {e}")
        return None

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


class AbstractBase(ABC):


    @abstractmethod
    def save(self, *args, **kwargs) -> None:
        """Forces child models to define save logic."""
        pass


    @abstractmethod
    def update(self, **kwargs) -> None:
        """Forces child models to define update logic."""
        pass


    @abstractmethod
    def delete(self, *args, **kwargs) -> None:
        """Forces child models to define delete logic."""
        pass


class BaseModel(models.Model, AbstractBase):
    """Abstract base model with common CRUD methods."""

     # Attach the custom manager
    objects = BaseManager()


    class Meta:
        abstract = True  # This ensures Django doesn't create a table for BaseModel


    @classmethod
    def commit(cls) -> None:
        """Commit all pending changes in the database session."""

        try:
            transaction.commit()

        except Exception as e:
            transaction.rollback()
            logger.exception(f"Transaction commit failed: {e}")
            raise


    def before_update(self) -> None:
        """Hook to run custom logic before updating."""

        try:
            logger.info(f"Running before_update hook for {self.__class__.__name__}.")
        except Exception as e:
            logger.exception(f"Unexpected error in before_update for {self.__class__.__name__}: {e}")


    def after_update(self) -> None:
        """Hook to run custom logic after updating."""

        try:
            logger.info(f"Running after_update hook for {self.__class__.__name__}.")
        except Exception as e:
            logger.exception(f"Unexpected error in after_update for {self.__class__.__name__}: {e}")


    def update(self, **kwargs) -> None:
        """Update model fields and save the instance safely."""

        try:
            self.before_update()

            for attr, value in kwargs.items():
                setattr(self, attr, value)
            self.save()

            self.after_update()

        except Exception as e:
            logger.exception(f"Error updating {self.__class__.__name__}: {e}")
            raise e


    def before_save(self) -> None:
        """Hook to run custom logic before saving."""

        try:
            logger.info(f"Running before_save hook for {self.__class__.__name__}.")
        except Exception as e:
            logger.exception(f"Unexpected error in before_save for {self.__class__.__name__}: {e}")


    def after_save(self) -> None:
        """Hook to run custom logic after saving."""

        try:
            logger.info(f"Running after_save hook for {self.__class__.__name__}.")
        except Exception as e:
            logger.exception(f"Unexpected error in after_save for {self.__class__.__name__}: {e}")


    def save(self, commit: bool = False, *args, **kwargs) -> None:

        """Save instance with transaction handling."""

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
