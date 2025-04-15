from __future__ import annotations

# External
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import validate_ipv46_address
from django.db.models import Index
from django.contrib.postgres.indexes import GinIndex


# Internal
from ..accounts.models import Account
from ..questionnaires.models import Question, Questionnaire
from ...common.base_model import BaseModel
from .validators import QuestionResponseValidator
from typing import cast


class QuestionnaireSubmission(BaseModel):
    """
    Tracks an account's submission of a questionnaire (whether complete or in progress).
    """

    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT, # Never delete accounts with submissions
        related_name='questionnaire_submissions',
        verbose_name=_("Account"),
        help_text=_("The account that submitted or is completing the questionnaire.")
    )
    questionnaire = models.ForeignKey(
        Questionnaire,
        on_delete=models.PROTECT, # Don’t allow deleting forms with user data
        related_name='submissions',
        verbose_name=_("Questionnaire"),
        help_text=_("The questionnaire being filled.")
    )
    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Started At"),
        help_text=_("When the questionnaire session began.")
    )
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_("Submitted At"),
        help_text=_("When the questionnaire was officially submitted (must be in year/month/days).")
    )
    is_submitted = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_("Is Submitted"),
        help_text=_("Whether the user has submitted the form.")
    )
    was_assigned = models.BooleanField(
        default=False,
        verbose_name=_("Was Assigned"),
        help_text=_("True if the questionnaire was assigned by the business.")
    )
    ip_address = models.GenericIPAddressField(
        protocol='both',
        unpack_ipv4=True,
        validators=[validate_ipv46_address],
        verbose_name=_("IP Address"),
        help_text=_("IP address of the client submitting the form.")
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Metadata"),
        help_text=_("Optional context like browser, device, geolocation, etc.")
    )

    class Meta:
        verbose_name = _("Questionnaire Submission")
        verbose_name_plural = _("Questionnaire Submissions")
        ordering = ['-submitted_at']
        unique_together = ('account', 'questionnaire')

        indexes = [
            Index(
                fields=["is_submitted"],
                name="submitted_only",
                condition=models.Q(is_submitted=True)
            ),
            Index(
                fields=["account", "is_submitted"],
                name="idx_account_submitted"
            ),
            Index(
                fields=["submitted_at"],
                name="idx_submission_date"
            )
        ]


    def __str__(self):
        return f"{self.account} submission for {self.questionnaire} ({'submitted' if self.is_submitted else 'draft'})"


class QuestionResponse(BaseModel):
    """
    Stores individual responses to questions within a questionnaire submission.
    """

    submission = models.ForeignKey(
        QuestionnaireSubmission,
        on_delete=models.CASCADE, # Clean up answers when a submission is deleted
        related_name='answers',
        verbose_name=_("Submission"),
        help_text=_("The questionnaire submission this answer belongs to.")
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.PROTECT, # Questions are shared and should not be deleted if answered
        related_name='responses',
        verbose_name=_("Question"),
        help_text=_("The question being answered.")
    )
    payload = models.JSONField(
        verbose_name=_("Answer"),
        help_text=_("The actual response content (text, choices, file reference, etc.)")
    )
    answered_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Answered At"),
        help_text=_("When the answer was recorded.")
    )


    class Meta:
        verbose_name = _("QuestionResponse")
        verbose_name_plural = _("QuestionResponses")
        ordering = ['-answered_at']

        indexes = [
            Index(
                fields=['submission'],
                name='idx_by_submission'
            ),
            Index(
                fields=['question'],
                name='idx_by_question'
            ),
            # Partial Filtering only on completed data
            # Index(
            #     fields=['submitted_at'],
            #     name='complete_responses_idx',
            #     condition=Q(is_complete=True)
            # ),

            # JSONB GIN index on payload for optional filtering
            GinIndex(fields=['payload'], name='payload_gin_idx'),

        ]

        # constraints = [
        #     # Uniqueness on completed question responses,  Preventing duplicates on completed answers
        #     models.UniqueConstraint(
        #         fields=['account', 'question'],
        #         name='unique_completed_answer',
        #         condition=Q(is_complete=True),
        #         deferrable=models.Deferrable.DEFERRED
        #     )
        # ]

    def __str__(self) -> str:
        submission: QuestionnaireSubmission = cast(QuestionnaireSubmission, self.submission)
        question: Question = cast(Question, self.question)

        account_label = str(submission.account)
        questionnaire_label = str(submission.questionnaire)
        question_label = question.reference_code
        payload_value = self.payload if isinstance(self.payload, str) else str(self.payload)

        return f"{account_label} on \"{questionnaire_label}\" for \"{question_label}\": {payload_value}"


    @property
    def response_summary(self):
        """Extracts a safe string representation of the payload"""

        if isinstance(self.payload, dict):
            return str(list(self.payload.values())[0])[:100]
        return str(self.payload)[:100]


    def clean(self):
        """
        Validates a single question response:
        - Required fields are filled
        - Payload matches question rules
        """
        errors = {}

        question = cast(Question, self.question)
        answer = self.payload

        # Rule: Required questions must have a value
        if question.is_required and (answer is None or answer == ""):
            errors["answer"] = _("This question requires a response.")

        # Rule: Payload must match validation rules for this question
        try:
            res = QuestionResponseValidator(question, answer)
            res.validate()
        except ValidationError as e:
            errors["answer"] = e.messages  # or e.message_dict if multiple fields

        if errors:
            raise ValidationError(errors)
