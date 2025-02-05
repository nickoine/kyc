from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Type, Tuple
    from .models import Account, Admin, User, Role

def get_accounts_models() -> "Tuple[Type[Account], Type[Admin], Type[User], Type[Role]]":
    from .models import Account, Admin, User, Role
    return Account, Admin, User, Role
