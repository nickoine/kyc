from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import validate_ipv46_address
from ..accounts.models import Account
from ..questionnaires.models import Question
from ...common.base_model import BaseModel

class UserResponse(BaseModel):
    """
    Tracks user-submitted responses to questionnaire questions with full audit capability.
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
        related_name='user_responses',
        db_index=True,
        verbose_name=_("Question"),
        help_text=_("The question being responded to.")
    )
    payload = models.JSONField(
        verbose_name=_("Response Content"),
        db_index=True,
        help_text=_("Structured response data (text, choices, file references, etc.).")
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
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['account', 'question']), # Composite index
            models.Index(fields=['payload', 'submitted_at']),
            #UserResponse.objects.filter(is_complete=True).order_by('-submitted_at')
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['account', 'question'],
                condition=models.Q(is_complete=True),
                name='unique_complete_response_per_question'
            )
        ]

    def __str__(self):
        return _("Response #%(id)s by %(account)s") % {
            'id': self.id,
            'account': self.account
        }

    @property
    def response_summary(self):
        """Extracts a safe string representation of the payload"""

        if isinstance(self.payload, dict):
            return str(list(self.payload.values())[0])[:100]
        return str(self.payload)[:100]

    # def clean(self):
    #     """Validates the payload against question validation_rules"""
    #     from .services import validate_response_payload
    #     if not self.payload:
    #         raise ValidationError(_("Response payload cannot be empty"))
    #     validate_response_payload(self.question, self.payload)
    #
    # def clean(self):
    #     # Validate payload against question type
    #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #         raise ValidationError({
    #             'payload': "Must be a number for this question"
    #         })
    #
    #     # Ensure required questions aren't empty
    #     if self.question.is_required and not self.payload:
    #         raise ValidationError("Response is required")


    # def clean(self):
    #     """Validates the payload against question validation_rules"""
    #     from .services import validate_response_payload
    #     if not self.payload:
    #         raise ValidationError(_("Response payload cannot be empty"))
    #     validate_response_payload(self.question, self.payload)
    #
    # def clean(self):
    #     # Validate payload against question type
    #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #         raise ValidationError({
    #             'payload': "Must be a number for this question"
    #         })
    #
    #     # Ensure required questions aren't empty
    #     if self.question.is_required and not self.payload:
    #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")    # def clean(self):
    #     #     """Validates the payload against question validation_rules"""
    #     #     from .services import validate_response_payload
    #     #     if not self.payload:
    #     #         raise ValidationError(_("Response payload cannot be empty"))
    #     #     validate_response_payload(self.question, self.payload)
    #     #
    #     # def clean(self):
    #     #     # Validate payload against question type
    #     #     if self.question.type == 'number' and not str(self.payload).isdigit():
    #     #         raise ValidationError({
    #     #             'payload': "Must be a number for this question"
    #     #         })
    #     #
    #     #     # Ensure required questions aren't empty
    #     #     if self.question.is_required and not self.payload:
    #     #         raise ValidationError("Response is required")