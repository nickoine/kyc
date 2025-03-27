# External
from __future__ import annotations
from django.db import transaction

# Internal
from ..shared import BaseRepository
from .models import User, Account, Admin

from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from typing import Optional, List, Type


class UserRepository(BaseRepository[User]):
    """Repository for handling User model operations."""


    def __init__(self, model: Type[User] = User, cache_enabled: bool = True):
        self._model = model
        self._cache_enabled = cache_enabled


    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Fetch a user by ID with caching."""
        return self.get_by_id(user_id)


    def get_all_users(self) -> List[User]:
        """Retrieve all users."""
        return self.get_all()


    @transaction.atomic
    def create_user(self, **kwargs) -> Optional[User]:
        """Create a new user within an atomic transaction and clear cache."""
        return self.create(**kwargs)


    @transaction.atomic
    def update_user_by_id(self, user_id: int, **kwargs) -> Optional[User]:
        """Update a user by ID atomically and refresh cache."""
        return self.update(user_id, **kwargs)


    @transaction.atomic
    def delete_user_by_id(self, user_id: int) -> bool:
        """Delete a user by ID atomically and clear cache."""
        return self.delete(user_id)


    @transaction.atomic
    def bulk_create_users(self, users: List[User]) -> List[User]:
        """Bulk create user instances atomically."""
        return self.bulk_create(users)


    @transaction.atomic
    def bulk_update_users(self, users: List[User], fields: List[str]) -> List[User]:
        """Bulk update user instances atomically."""
        return self.bulk_update(users, fields)


    @transaction.atomic
    def bulk_delete_users(self, **filters) -> Tuple[List[User], int]:
        """Bulk delete users atomically based on filters."""
        return self.bulk_delete(**filters)


    def get_verified_users(self) -> List[User]:
        """Retrieve all verified users."""
        return list(self.manager.filter_by(is_verified=True))


    def get_unverified_users(self) -> List[User]:
        """Retrieve all unverified users."""
        return list(self.manager.filter_by(is_verified=False))


class AccountRepository(BaseRepository[Account]):
    """Repository for handling Account model operations."""
    pass

class AdminRepository(BaseRepository[Admin]):
    """Repository for handling User model operations."""
    pass