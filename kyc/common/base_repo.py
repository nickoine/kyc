from __future__ import annotations

# External
from django.db import models
from django.db import transaction

# Internal
from abc import ABC, abstractmethod
from typing import Optional, List, Type, TypeVar, Generic, Tuple, ClassVar
from .base_cache import CacheManager
from .base_model import DBManager


T = TypeVar("T", bound=models.Model)


class Repository(ABC):
    """Abstract class that defines the contract for repositories."""

    _manager: DBManager[T] = None

    @property
    @abstractmethod
    def model(self) -> Type[T]:
        """Return the model class this repository works with."""
        pass


    @property
    def manager(self) -> DBManager[T]:
        """Return the manager instance for the model (lazy loaded)."""

        if self._manager is None:
            if not hasattr(self.model, "objects") or not isinstance(self.model.objects, models.Manager):
                raise TypeError(f"{self.model.__name__} must have a valid Manager.")
            self._manager = self.model.objects
        return self._manager


    @abstractmethod
    def get_entity_by_id(self, obj_id: int) -> Optional[T]:
        """Fetch an entity by ID."""
        pass


    @abstractmethod
    def get_all_entities(self) -> List[T]:
        """Fetch all entities."""
        pass


    @abstractmethod
    def create_entity(self, **kwargs) -> Optional[T]:
        """Create a new entity."""
        pass


    @abstractmethod
    def update_entity(self, obj_id: int, **kwargs) -> Optional[T]:
        """Update an entity."""
        pass


    @abstractmethod
    def delete_entity(self, obj_id: int) -> Optional[T]:
        """Delete an entity."""
        pass


    @abstractmethod
    def bulk_create_entities(self, instances: List[T]) -> List[T]:
        """Bulk create new entities."""
        pass


    @abstractmethod
    def bulk_update_entities(self, instances: List[T], fields: List[str]) -> List[T]:
        """Bulk update entities."""
        pass


    @abstractmethod
    def bulk_delete_entities(self, instances: List[T], **filters) -> Tuple[List[T], int]:
        """Bulk delete entities."""
        pass


class BaseRepository(Generic[T], Repository):
    """Base repository implementation with caching."""

    CACHE_TIMEOUT = 60 * 15
    CACHE_KEY_FORMAT: ClassVar[str] = "{app_label}.{model_name}.{id}"

    _model: Type[T] = None
    _cache_enabled: bool = False
    _cache_manager: CacheManager = CacheManager()


    def __init__(self, model: Type[T], cache_enabled: bool = False) -> None:
        """Initialize repository with a model and caching option."""
        self._model = model
        self._cache_enabled = cache_enabled


    @property
    def model(self) -> Type[T]:
        return self._model


    @property
    def cache_enabled(self) -> bool:
        return self._cache_enabled


    def _get_cache_key(self, obj_id: int) -> str:
        """Generate a cache key for the given instance."""
        return f"{self.model.__name__.lower()}:{obj_id}"


    def get_entity_by_id(self, obj_id: int) -> Optional[T]:
        """Fetch a single model instance by its ID with caching."""

        cache_key = self._get_cache_key(obj_id)
        if self._cache_enabled:
            instance = self._cache_manager.get(cache_key)
            if instance:
                return instance

        instance = self.manager.get_by_id(obj_id)
        if instance and self._cache_enabled:
            self._cache_manager.set(cache_key, instance, timeout=self.CACHE_TIMEOUT)
        return instance


    def get_all_entities(self) -> List[T]:
        """Fetch all instances with optional caching."""

        cache_key = f"{self.model.__name__.lower()}_all"
        if self._cache_enabled:
            return self._cache_manager.get_or_set(
                cache_key, lambda: list(self.manager.get_all()), timeout=600
            )
        return list(self.manager.get_all())


    @transaction.atomic
    def create_entity(self, **kwargs) -> Optional[T]:
        """Create an instance and invalidate relevant cache."""

        instance = self.manager.create_instance(**kwargs)
        if self._cache_enabled and instance:
            self._cache_manager.delete(self._get_cache_key(instance.id))
        return instance


    @transaction.atomic
    def update_entity(self, obj_id: int, **kwargs) -> Optional[T]:
        """Update an instance and clear relevant cache."""

        instance = self.manager.get_by_id(obj_id)
        if not instance:
            return None

        instance.update(**kwargs)
        if self._cache_enabled:
            self._cache_manager.delete(self._get_cache_key(obj_id))
        return instance


    @transaction.atomic
    def delete_entity(self, obj_id: int) -> Optional[T]:
        """Delete an instance and remove from cache."""

        instance = self.manager.get_by_id(obj_id)
        if not instance:
            return None

        instance.delete()
        if self._cache_enabled:
            self._cache_manager.delete(self._get_cache_key(obj_id))
        return instance


    @transaction.atomic
    def bulk_create_entities(self, instances: List[T]) -> List[T]:
        """Bulk create multiple instances."""

        if not instances:
            return []

        created_instances = self.manager.bulk_create_instances(instances)
        if self._cache_enabled:
            for instance in created_instances:
                self._cache_manager.delete(self._get_cache_key(instance.id))
        return created_instances


    @transaction.atomic
    def bulk_update_entities(self, instances: List[T], fields: List[str]) -> List[T]:
        """Bulk update multiple instances."""

        if not instances:
            return []

        updated_instances = self.manager.bulk_update_instances(instances, fields)
        if self._cache_enabled:
            for instance in updated_instances:
                self._cache_manager.delete(self._get_cache_key(instance.id))
        return updated_instances


    @transaction.atomic
    def bulk_delete_entities(self, instances: List[T], **filters) -> Tuple[List[T], int]:
        """Bulk delete multiple instances."""

        if not instances:
            return [], 0

        deleted_instances = self.manager.bulk_delete_instances(**filters)
        deleted_count = len(deleted_instances)

        if self._cache_enabled:
            for instance in deleted_instances:
                self._cache_manager.delete(self._get_cache_key(instance.id))

        return deleted_instances, deleted_count
