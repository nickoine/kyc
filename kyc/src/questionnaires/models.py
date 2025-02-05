# External
from django.db import models

# Internal
from ...common.base_model import BaseModel


class Questionnaire(BaseModel):
    """
    Represents a questionnaire in the system.
    Each questionnaire can have multiple questions and can be associated with multiple accounts.
    """
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'
        ARCHIVED = 'archived', 'Archived'

    questionnaire_name = models.CharField(
        max_length=255,
        verbose_name="Name",
        help_text="The name of the questionnaire.",
        db_index=True  # Index for faster lookups
    )
    questionnaire_type = models.CharField(
        max_length=50,
        verbose_name="Type",
        help_text="The type of questionnaire (e.g., survey, feedback)."
    )
    questionnaire_category = models.CharField(
        max_length=50,
        verbose_name="Category",
        help_text="The category of the questionnaire (e.g., financial, personal)."
    )
    questionnaire_language = models.JSONField(
        default=list,
        verbose_name="Supported Languages",
        help_text="A list of languages supported by the questionnaire."
    )
    questionnaire_description = models.TextField(
        verbose_name="Description",
        help_text="A detailed description of the questionnaire."
    )
    questionnaire_status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name="Status",
        help_text="The current status of the questionnaire.",
        db_index=True  # Index for faster filtering by status
    )
    questionnaire_created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
        help_text="The timestamp when the questionnaire was created."
    )
    questionnaire_deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Deleted At",
        help_text="The timestamp when the questionnaire was deleted (optional)."
    )

    class Meta:
        verbose_name = "Questionnaire"
        verbose_name_plural = "Questionnaires"
        ordering = ['questionnaire_name']

    def __str__(self):
        return self.questionnaire_name


class Question(BaseModel):
    """
    Represents a question in the system.
    Each question can belong to multiple questionnaires.
    """
    question_questionnaires = models.ManyToManyField(
        Questionnaire,
        related_name='questions',
        verbose_name="Questionnaires",
        help_text="The questionnaires this question belongs to."
    )
    question_name = models.CharField(
        max_length=255,
        verbose_name="Question Text",
        help_text="The text of the question.",
        db_index=True  # Index for faster lookups
    )
    question_description = models.TextField(
        verbose_name="Description",
        help_text="A detailed description of the question."
    )
    question_type = models.CharField(
        max_length=50,
        verbose_name="Type",
        help_text="The type of question (e.g., text, multiple-choice)."
    )
    question_created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
        help_text="The timestamp when the question was created."
    )

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ['question_name']

    def __str__(self):
        return self.question_name
