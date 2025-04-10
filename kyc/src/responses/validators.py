# kyc/validators.py

from django.core.exceptions import ValidationError
from typing import Any
from ..questionnaires.models import Question


class QuestionResponseValidator:
    """
    Simple pluggable validator for QuestionResponses.
    Will be extended later to support full validation_rules config.
    """

    def __init__(self, question: Question, answer: Any) -> None:
        self.question = question
        self.answer = answer


    def validate(self):
        q_type = self.question.type

        if q_type == Question.Type.TEXT:
            if not isinstance(self.answer, str):
                raise ValidationError("Answer must be a string.")


        elif q_type == Question.Type.DATE:
            # You could add regex or date parsing here later
            if not isinstance(self.answer, str) or len(self.answer) != 10:
                raise ValidationError("Answer must be a valid ISO date string (YYYY-MM-DD).")


        elif q_type == Question.Type.MULTIPLE_CHOICE:
            if not isinstance(self.answer, list):
                raise ValidationError("Answer must be a list of selected options.")


        elif q_type == Question.Type.FILE_UPLOAD:
            if not isinstance(self.answer, str):
                raise ValidationError("File uploads must be provided as string file references.")


        if self.question.validation_rules:
            # TODO: extend this later with rule parsing
            pass
