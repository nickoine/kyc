# External
from __future__ import annotations
from django.core.cache import cache
from django.db.models import Manager, Model
from django.db.models.options import Options
from django.db import transaction

# Internal
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, List, Type, TypeVar, Generic, Tuple, ClassVar
from kyc.common import BaseModel

if TYPE_CHECKING:
    from kyc.common import BaseManager


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
        pass


    @abstractmethod
    def bulk_update_entities(self, instances: List[T], fields: List[str]) -> List[T]:
        pass


    @abstractmethod
    def bulk_delete_entities(self, instances: List[T], **filters) -> Tuple[List[T], int]:
        pass


class BaseRepository(Repository[T]):
    """Base repository implementation."""

    CACHE_TIMEOUT = 60 * 15
    CACHE_KEY_FORMAT: ClassVar[str] = "{app_label}.{model_name}.{id}"

    _model: Type[T] = None
    _cache_enabled: bool = False


    def __init__(self, model: Type[T], cache_enabled: bool = False):
        """Initialize repository with a model and caching option."""
        self._model = model
        self._cache_enabled = cache_enabled


    @property
    def model(self) -> Type[T]:
        return self._model


    @property
    def cache_enabled(self) -> bool:
        return self._cache_enabled


    @staticmethod
    def _get_cache_key(instance: T) -> str:
        """Static cache key generator."""

        meta: Options = instance._meta  # type: ignore[attr-defined]
        return BaseRepository.CACHE_KEY_FORMAT.format(
            app_label=meta.app_label,
            model_name=meta.model_name,
            id=instance.id
        )


    def get_entity_by_id(self, obj_id: int) -> Optional[T]:
        """Fetch a single model instance by its ID."""

        cache_key = f"{self.model.__name__.lower()}:{obj_id}"
        if self._cache_enabled and (cached := cache.get(cache_key)):  # Walrus operator for readability
            return cached

        instance = self.manager.get_by_id(obj_id)
        if instance and self._cache_enabled:
            cache.set(self._get_cache_key(instance), instance, timeout=self.CACHE_TIMEOUT)
        return instance


    def get_all_entities(self) -> List[T]:
        """Fetch all instances."""

        if self._cache_enabled:
            return cache.get_or_set(
                f"{self.model.__name__.lower()}_all", lambda: list(self.manager.get_all()), timeout=600
            )  # Cache for 10 minutes
        return list(self.manager.get_all())


    @transaction.atomic
    def create_entity(self, **kwargs) -> Optional[T]:
        """Create an instance and invalidate relevant cache."""

        instance = self.manager.create_instance(**kwargs)

        if self._cache_enabled and instance:
            model_name = self.model.__name__.lower()
            version_key = f"{model_name}_cache_version"

            # Update cache version atomically
            cache_version = cache.incr(version_key, delta=1) if cache.get(version_key) else 1
            cache.set(version_key, cache_version)

            # Remove only necessary cache keys
            cache.delete(f"{model_name}_all")
            if isinstance(instance, BaseModel):
                cache.delete(self._get_cache_key(instance))

        return instance


    @transaction.atomic
    def update_entity(self, obj_id: int, **kwargs) -> Optional[T]:
        """Update an instance and clear relevant cache."""

        instance = self.manager.get_by_id(obj_id)
        if not instance:
            return None

        instance.update(**kwargs)
        if self._cache_enabled:
            cache.delete(self._get_cache_key(instance))
        return instance


    @transaction.atomic
    def delete_entity(self, obj_id: int) -> Optional[T]:
        """Delete an instance and remove from cache."""

        instance = self.manager.get_by_id(obj_id)
        if not instance:
            return None

        instance.delete()
        if self._cache_enabled:
            cache.delete(self._get_cache_key(instance))
        return instance


    @transaction.atomic
    def bulk_create_entities(self, instances: List[T]) -> List[T]:
        """Bulk create multiple instances."""

        if not instances:
            return []

        created_instances = self.manager.bulk_create_instances(instances)
        if self._cache_enabled:
            cache.delete(f"{self.model.__name__.lower()}_all")
        return created_instances or []


    @transaction.atomic
    def bulk_update_entities(self, instances: List[T], fields: List[str]) -> List[T]:  # Removed Optional
        """Bulk update multiple instances."""
        if not instances:
            return []

        updated_instances = self.manager.bulk_update_instances(instances, fields)
        if self._cache_enabled:
            cache.delete(f"{self.model.__name__.lower()}_all")
        return updated_instances or []


    @transaction.atomic
    def bulk_delete_entities(self, instances: List[T], **filters) -> Tuple[List[T], int]:
        """Bulk delete multiple instances."""
        if not instances:
            return [], 0

        deleted_instances = self.manager.bulk_delete_instances(**filters)
        deleted_count = len(deleted_instances)

        if self._cache_enabled:
            cache.delete(f"{self.model.__name__.lower()}_all")

        # This tells the type checker that we know these are the correct type
        typed_deleted_instances: List[T] = deleted_instances  # type: ignore
        return typed_deleted_instances, deleted_count
