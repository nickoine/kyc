from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from kyc.src.questionnaires import Question

#todo: review
class ResponseValidator:
    """Validates complete questionnaire responses against defined questions"""

    def __init__(self, questionnaire):
        self.questionnaire = questionnaire
        self.questions = questionnaire.questions.all()
        self.required_codes = {
            q.reference_code for q in self.questions if q.is_required
        }


    def validate(self, payload) -> None:
        """Validate complete response payload against questionnaire"""

        errors = {}

        # Structural validation
        self._validate_payload_structure(payload, errors)
        if errors:
            raise ValidationError(errors)

        # Question-level validation
        for question in self.questions:
            self._validate_question_response(question, payload, errors)

        if errors:
            raise ValidationError(errors)


    def _validate_payload_structure(self, payload, errors):
        """Check payload meets basic requirements"""

        if not isinstance(payload, dict):
            errors['payload'] = _("Payload must be a dictionary")
            return

        missing_required = self.required_codes - set(payload.keys())
        for code in missing_required:
            errors[code] = _("This field is required")


    def _validate_question_response(self, question, payload, errors):
        """Validate individual question response"""

        response = payload.get(question.reference_code)

        # Skip validation if empty and not required
        if response in [None, ""] and not question.is_required:
            return

        validator = self._get_question_validator(question.type)
        validator(question, response, errors)


    def _get_question_validator(self, q_type):
        """Get type-specific validation method"""

        return {
            Question.Type.TEXT: self._validate_text,
            Question.Type.MULTIPLE_CHOICE: self._validate_choice,
            Question.Type.FILE_UPLOAD: self._validate_file,
            Question.Type.DATE: self._validate_date,
        }.get(q_type, lambda *_: None)


    @staticmethod
    # Type-specific validators
    def _validate_text(question, value, errors):
        rules = question.validation_rules or {}
        if not isinstance(value, str):
            errors[question.reference_code] = _("Must be text")
            return

        if (min_len := rules.get('min_length')) and len(value) < min_len:
            errors[question.reference_code] = _(f"Minimum {min_len} characters")

        if (max_len := rules.get('max_length')) and len(value) > max_len:
            errors[question.reference_code] = _(f"Maximum {max_len} characters")


    @staticmethod
    def _validate_choice(question, value, errors):
        rules = question.validation_rules or {}
        valid_choices = set(rules.get('choices', []))

        if not valid_choices:
            return

        user_choices = [value] if not isinstance(value, list) else value

        if not all(choice in valid_choices for choice in user_choices):
            errors[question.reference_code] = _("Invalid selection")


    @staticmethod
    def _validate_file(question, value, errors):
        if not isinstance(value, str):
            errors[question.reference_code] = _("Must be file reference")


    @staticmethod
    def _validate_date(question, value, errors):
        try:
            # Add proper date parsing/validation logic
            if not isinstance(value, str):  # Basic check
                errors[question.reference_code] = _("Invalid date format")
        except ValueError:
            errors[question.reference_code] = _("Invalid date value")