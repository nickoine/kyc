from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Type, Tuple
    from .models import Account, User

def get_accounts_models() -> "Tuple[Type[Account], Type[User]]":
    from .models import Account, User
    return Account, User
