from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Type, Tuple
    from .models import Questionnaire, Question

def get_questionnaires_models() -> "Tuple[Type[Questionnaire], Type[Question]]":
    from .models import Questionnaire, Question
    return Questionnaire, Question
