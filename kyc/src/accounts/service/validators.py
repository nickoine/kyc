# services/validators.py
from django.core.exceptions import ValidationError


def validate_question_response(question, response):
    rules = question.validation_rules

    if question.type == "text":
        if len(response) < rules.get("min_length", 0):
            raise ValidationError(f"Must be at least {rules['min_length']} characters")

        if "regex" in rules:
            import re
            if not re.match(rules["regex"], response):
                raise ValidationError("Invalid format")

    elif question.type == "file":
        if response.size > rules.get("max_size", 0):
            raise ValidationError(f"File too large (max {rules['max_size']} bytes)")

    # Add other question types...