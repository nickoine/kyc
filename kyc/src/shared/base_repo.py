# External
from django.core.cache import cache
from django.db.models import Model, Manager

# Internal
from abc import ABC, abstractmethod
from typing import Optional, List, Type, TypeVar, Generic, Tuple
from ...common import BaseManager


T = TypeVar("T", bound=Model)


class Repository(ABC, Generic[T]):
    """Abstract class that defines the contract for repositories."""

    @property
    @abstractmethod
    def model(self) -> Type[T]:
        """Return the model class this repository works with."""
        pass


    @property
    def manager(self) -> BaseManager[T]:
        """Return the manager instance for the model."""

        if not hasattr(self.model, "objects") or not isinstance(self.model.objects, Manager):
            raise TypeError(f"{self.model.__name__} must have a valid Manager.")
        return self.model.objects


    @abstractmethod
    def get_by_id(self, obj_id: int) -> Optional[Model]:
        """Fetch an instance by ID."""
        pass


    @abstractmethod
    def get_all(self) -> List[Model]:
        """Fetch all instances."""
        pass


    @abstractmethod
    def create(self, **kwargs) -> Optional[Model]:
        """Create a new instance."""
        pass


    @abstractmethod
    def update(self, obj_id: int, **kwargs) -> Optional[Model]:
        """Update an instance."""
        pass


    @abstractmethod
    def delete(self, obj_id: int) -> bool:
        """Delete an instance."""
        pass


class BaseRepository(Repository[T]):
    """Concrete base repository implementation."""

    CACHE_TIMEOUT = 60 * 15
    _model, _cache_enabled = None, False


    @property
    def model(self) -> Type[T]:
        return self._model


    @property
    def cache_enabled(self) -> bool:
        return self._cache_enabled


    def get_by_id(self, obj_id: int) -> Optional[T]:
        """Fetch a single model instance by its ID."""

        cache_key = f"{self.model.__name__.lower()}:{obj_id}"
        if self.cache_enabled:
            if cached := cache.get(cache_key): # walrus operator
                return cached

        instance = self.manager.get_by_id(obj_id)
        if instance and self.cache_enabled:
            cache.set(cache_key, instance, timeout=self.CACHE_TIMEOUT)
        return instance


    def get_all(self) -> List[T]:
        """Fetch all instances."""
        return list(self.manager.get_all())


    def create(self, **kwargs) -> Optional[Model]:
        """Create an instance and invalidate related cache."""

        instance = self.manager.create_instance(**kwargs)
        if instance and self.cache_enabled:
            cache.delete_pattern(f"{self.model.__name__.lower()}*")  # Invalidate cache operations to prevent stale data
        return instance


    def update(self, obj_id: int, **kwargs) -> Optional[Model]:
        """Update an instance and clear relevant cache."""

        instance = self.manager.get_by_id(obj_id)
        if not instance:
            return None

        instance.update(**kwargs)  # Calls BaseModel.update()
        if self.cache_enabled:
            cache.delete(f"{self.model.__name__.lower()}:{obj_id}")
        return instance


    def delete(self, obj_id: int) -> bool:
        """Delete an instance and remove from cache."""

        instance = self.manager.get_by_id(obj_id)
        if not instance:
            return False

        instance.delete(obj_id)
        if self.cache_enabled:
            cache.delete(f"{self.model.__name__.lower()}:{obj_id}")
        return True


    def bulk_create(self, instances: List[T]) -> List[T]:
        """Bulk create multiple instances."""

        created_instances = self.manager.bulk_create_instances(instances)
        if self.cache_enabled:
            cache.delete_pattern(f"{self.model.__name__.lower()}*")  # Invalidate related cache
        return created_instances


    def bulk_update(self, instances: List[T], fields: List[str]) -> List[T]:
        """Bulk update multiple instances."""

        if instances:
            updated_instances = self.manager.bulk_update_instances(instances, fields)
            if self.cache_enabled:
                cache.delete_pattern(f"{self.model.__name__.lower()}*")  # Clear stale cache
            return  updated_instances


    def bulk_delete(self, **filters) -> Tuple[List[T], int]:
        """Bulk delete multiple instances."""

        deleted_instances = self.manager.bulk_delete_instances(**filters)
        deleted_count = len(deleted_instances)

        if self.cache_enabled:
            cache.delete_pattern(f"{self.model.__name__.lower()}*")

        return deleted_instances, deleted_count
