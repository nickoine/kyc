# External
from django.db import models

# Internal
from ..accounts.models import Account
from ..questionnaires.models import Questionnaire, Question
from ...common.base_model import BaseModel


class UserResponse(BaseModel):
    """
    Represents a user's response to a question in a questionnaire.
    Each response is linked to an account, a questionnaire, and a question.
    """
    response_account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        verbose_name="Account",
        help_text="The account that submitted the response."
    )
    response_questionnaire = models.ForeignKey(
        Questionnaire,
        on_delete=models.CASCADE,
        verbose_name="Questionnaire",
        help_text="The questionnaire the response belongs to."
    )
    response_question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name="Question",
        help_text="The question the response is for."
    )
    response_data = models.JSONField(
        verbose_name="Response Data",
        help_text="The structured data of the response."
    )
    response_submitted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Submitted At",
        help_text="The timestamp when the response was submitted.",
        db_index=True  # Index for faster sorting by submission time
    )

    class Meta:
        verbose_name = "User Response"
        verbose_name_plural = "User Responses"
        ordering = ['-response_submitted_at']


    def __str__(self) -> str:
        return (f"Response is {self.response_data}. By Account {self.response_account}"
                f" on {self.response_question} from {self.response_questionnaire} .")
