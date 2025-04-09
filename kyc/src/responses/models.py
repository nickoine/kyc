from __future__ import annotations

# External
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import TruncMonth
from django.utils.translation import gettext_lazy as _
from django.core.validators import validate_ipv46_address
from django.contrib.postgres.indexes import GinIndex, BrinIndex


# Internal
from ..accounts.models import Account
from ..questionnaires.models import Question, Questionnaire
from ...common.base_model import BaseModel
from .validators import ResponseValidator
from typing import cast


class UserResponse(BaseModel):
    """
    User-submitted responses to questionnaire questions with full audit capability.
    Supports structured response data with validation against question rules.
    """

    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        db_index=True,
        related_name='responses',
        verbose_name=_("Account"),
        help_text=_("The account that submitted this response.")
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.PROTECT,  # Prevent question deletion if responses exist
        related_name='responses',
        db_index=True,
        verbose_name=_("Question"),
        help_text=_("The question being responded to.")
    )
    questionnaire = models.ForeignKey(
        Questionnaire,
        on_delete=models.PROTECT,
        related_name="responses",
        db_index=True,
        verbose_name=_("Questionnaire"),
        help_text=_("The questionnaire being responded to.")
    )
    payload = models.JSONField(
        verbose_name=_("Response Content"),
        db_index=True,
        help_text=_("Structured response data (text, choices, file references, etc.).")
    )
    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Started At"),
        help_text=_("When the user started this response.")
    )
    was_assigned = models.BooleanField(
        default=False,
        verbose_name=_("Was Assigned"),
        help_text=_("True if this questionnaire was required by the business.")
    )
    is_submitted = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_("Is Submitted"),
        help_text=_("Marks whether the questionnaire was completed and submitted.")
    )
    submitted_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name=_("Submitted At"),
        help_text=_("When the response was officially submitted.")
    )
    ip_address = models.GenericIPAddressField(
        protocol='both',
        unpack_ipv4=True,
        validators=[validate_ipv46_address],
        verbose_name=_("IP Address"),
        help_text=_("The IP address used when submitting.")
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Response Metadata"),
        help_text=_("Additional context (user_agent, geolocation, etc.)")
    )

    class Meta:
        verbose_name = _("User Response")
        verbose_name_plural = _("User Responses")
        ordering = ['-submitted_at']  # Default ordering for queries

        indexes = [
            # 1. Composite Index (Account+Question)
            models.Index(
                fields=['account', 'question'],
                name='account_question_composite_idx',
                # 7. Covering Index (INCLUDE)
                include=['submitted_at']  # PostgreSQL only
            ),

            # 2. Partial Index (Filtered)
            models.Index(
                fields=['is_complete', '-submitted_at'],
                name='complete_responses_desc_idx',
                # 5. Conditional Indexing
                condition=models.Q(is_complete=True),
                # 6. Descending Order
                opclasses=['bool_ops', 'datetime_ops DESC']  # PostgreSQL-specific
            ),

            # 3. JSONB GIN Index (Payload Search)
            GinIndex(
                fields=['payload'],
                name='payload_gin_idx',
                # 9. Specialized Ops Class
                opclasses=['jsonb_path_ops']  # Optimized JSON queries
            ),

            # 4. BRIN Index (Large Timestamp Range)
            BrinIndex(
                fields=['submitted_at'],
                name='submitted_at_brin_idx',
                pages_per_range=16  # Balance scan speed/accuracy
            ),

            # 8. Functional Index (Date Trunc)
            models.Index(
                fields=['submitted_at'],
                name='submitted_month_idx',
                # PostgreSQL function-based index
                expressions=[TruncMonth('submitted_at')]
            )
        ]
        constraints = [
            # 10. Conditional Unique Constraint
            models.UniqueConstraint(
                fields=['account', 'question'],
                name='unique_complete_response_per_question',
                # 5. Partial Uniqueness
                condition=models.Q(is_complete=True),
                # 7. Covering Index (Implied)
                deferrable=models.Deferrable.DEFERRED  # For transaction safety
            )
        ]


    def __str__(self) -> str:
        account_label = str(self.account)

        questionnaire = cast(Questionnaire, self.questionnaire)
        question = cast(Question, self.question)

        questionnaire_label = f"{questionnaire.name} v{questionnaire.version}" if questionnaire else "Unknown Questionnaire"
        question_label = question.reference_code if question else "Unknown Question"

        payload_value = self.payload if isinstance(self.payload, str) else str(self.payload)

        return f"{account_label} on \"{questionnaire_label}\" for \"{question_label}\": {payload_value}"


    @property
    def response_summary(self):
        """Extracts a safe string representation of the payload"""

        if isinstance(self.payload, dict):
            return str(list(self.payload.values())[0])[:100]
        return str(self.payload)[:100]


# todo: review
    def clean(self):
        """Validates response against question constraints"""

        errors = {}
        question = cast(Question, self.question)

        # Skip validation for non-submitted responses
        if not self.is_submitted:
            return

        # Ensure payload is a dictionary
        if not isinstance(self.payload, dict):
            raise ValidationError({'payload': _("Response must be a dictionary")})

        # Get the decoded payload data
        payload_data = self.payload  # This is now a Python dict

        # Full questionnaire validation
        try:
            validator = ResponseValidator(self.questionnaire)
            validator.validate(payload_data)  # Pass the decoded dict
        except ValidationError as e:
            errors.update(e.message_dict)

        # Additional business rules
        if question.is_required and not payload_data.get(question.reference_code):
            errors[question.reference_code] = _("Response is required")

        if errors:
            raise ValidationError(errors)