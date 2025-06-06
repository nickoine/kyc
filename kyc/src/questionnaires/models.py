from django.db import models
from django.utils.translation import gettext_lazy as _
from ...common.base_model import BaseModel


class Questionnaire(BaseModel):
    """Represents a form with multiple questions."""

    STATUS_CHOICES = [('draft', 'Draft'), ('public', 'Public'), ('private', 'Private')]
    TYPE_CHOICES = [('regular', 'Regular'), ('verification', 'Verification')]

    name = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name=_("Name"),
        help_text=_("Unique identifier for the questionnaire (e.g., 'KYC Form 2025').")
    )

    group = models.ForeignKey(
        'QuestionnaireGroup',
        on_delete=models.SET_NULL,
        null=True
    )

    description = models.TextField(
        max_length=255,
        verbose_name=_("Description"),
        help_text=_("Purpose and instructions for respondents.")
    )

    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name=_("Type"),
        help_text=_("Classification of questionnaire type.")
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        db_index=True,
        verbose_name=_("Status"),
        help_text=_("Publication state of the questionnaire.")
    )

    question = models.ManyToManyField(
        'Question',
        related_name='questionnaire',
        through='QuestionnaireQuestion',
        blank=True,
        help_text="Questions included in this questionnaire"
    )

    question_group = models.ManyToManyField(
        'QuestionGroup',
        related_name='questionnaire_category',
        through='QuestionnaireQuestionGroup',
        blank=True,
        help_text="Questions category included in this questionnaire"

    )

    submitted_by = models.ManyToManyField(
        'Account',
        blank=True,
        related_name='submitted_questionnaires',
        help_text = "List of accounts IDs the questionnaire was submitted by"

    )

    assigned_to = models.ManyToManyField(
        'Account',
        blank=True,
        related_name='assigned_questionnaire',
        help_text = "List of accounts IDs the questionnaire is assigned to (private)"

    )

    created_by = models.ForeignKey(
        'Account',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_questionnaire'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("When this questionnaire was created.")
    )

    updated_by = models.ForeignKey(
        'Account',
        on_delete=models.SET_NULL,
        null=True,
        related_name='updated_questionnaire'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
        help_text=_("Last modification timestamp.")
    )

    # assigned_to_groups = models.ManyToManyField(
    #     'AccountGroups',
    #     blank=True
    # )
    #
    # supported_languages = models.JSONField(
    #     default=list,
    #     verbose_name=_("Supported Languages"),
    #     help_text=_("List of language codes (e.g., ['en', 'es']) for multilingual support.")
    # )


    class Meta:
        verbose_name = _("Questionnaire")
        verbose_name_plural = _("Questionnaires")
        ordering = ['-status', '-created_at']
        indexes = [
            models.Index(fields=['status', 'type']),
            models.Index(fields=['name', 'status']),
            models.Index(fields=['created_by', 'status']),
        ]
        # admin
        permissions = [
            ("can_publish_questionnaire", "Can publish questionnaire"),
            ("can_assign_questionnaire", "Can assign questionnaire to accounts"),
            ("can_update_questionnaire", "Can update questionnaire"),
        ]


    def __str__(self):
        return f"{self.name} (Type: {self.type}, Status: {self.status})"


class QuestionnaireGroup(BaseModel):
    """Questionnaires can be grouped in categories."""

    name = models.CharField(max_length=100, unique=True)


class Question(BaseModel):
    """
    Represents an individual question item that can be reused across multiple questionnaires.
    Supports various response types and validation rules.
    """

    QUESTION_TYPE_CHOICES = [
        ('text', 'Text Input'),
        ('multiple_choice', 'Multiple Choice'),
        ('file', 'File Upload'),
        ('date', 'Date Selector')
    ]

    type = models.CharField(
        max_length=50,
        choices=QUESTION_TYPE_CHOICES,
        db_index=True,
        verbose_name=_("Response Type"),
        help_text=_("Determines what input widget to display.")
    )

    reference_code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name=_("Reference Code"),
        help_text=_("Unique identifier for business logic (e.g., 'TAX_ID_VERIFICATION').")
    )

    description = models.TextField(
        max_length=255,
        verbose_name=_("Description"),
        help_text=_("Purpose and instructions for respondents.")
    )

    group = models.ForeignKey(
        'QuestionGroup',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    validation_rules = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Validation Rules"),
        help_text=_("Configurable validation (e.g., {'min_length': 2, 'max_length': 100}).")
    )

    questionnaire = models.ManyToManyField(
        'Questionnaire',
        through='QuestionnaireQuestion',
        related_name='questions',
        verbose_name=_("Questionnaires"),
        help_text=_("Forms where this question appears.")
    )

    created_by = models.ForeignKey(
        'Account',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_question'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("When this question was first defined.")
    )


    class Meta:
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['reference_code', 'type']),
            models.Index(fields=['group', 'type']),
            models.Index(fields=['created_by', 'created_at']),
        ]
        permissions = [
            ("can_create_question", "Can create questions"),
            ("can_assign_question", "Can assign questions to questionnaire"),
            ("can_bulk_upload_questions", "Can bulk upload questions"),
        ]

    def __str__(self):
        return f"Question [{self.reference_code}] ({self.type})"


class QuestionGroup(models.Model):
    """Questions can be grouped in categories."""

    name = models.CharField(max_length=100, unique=True)


class QuestionnaireQuestion(models.Model):
    questionnaire = models.ForeignKey('Questionnaire', on_delete=models.CASCADE)
    question = models.ForeignKey('Question', on_delete=models.PROTECT)

    class Meta:
        unique_together = ('questionnaire', 'question')


class QuestionnaireQuestionGroup(models.Model):
    questionnaire = models.ForeignKey('Questionnaire', on_delete=models.CASCADE)
    question_group = models.ForeignKey('QuestionGroup', on_delete=models.PROTECT)

    class Meta:
        unique_together = ('questionnaire', 'question_group')
