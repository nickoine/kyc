from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Type
    from .models import UserResponse

def get_user_response_model() -> "Type[UserResponse]":
    from .models import UserResponse
    return UserResponse
