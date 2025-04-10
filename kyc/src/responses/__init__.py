from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Type
    from .models import QuestionnaireSubmission, QuestionResponse

def get_user_response_model() -> "Type[QuestionnaireSubmission], Type[QuestionResponse]":
    from .models import QuestionnaireSubmission, QuestionResponse
    return QuestionnaireSubmission, QuestionResponse
