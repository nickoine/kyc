from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from ...common.base_model import BaseModel
from ..accounts.models import Account


class Questionnaire(BaseModel):
    """
    Represents a customizable form with multiple questions that can be assigned to accounts.
    Supports versioning, internationalization, and lifecycle management.
    """

    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        INACTIVE = 'inactive', _('Inactive')
        DRAFT = 'draft', _('Draft')

    class Category(models.TextChoices):
        FINANCIAL = 'financial', _('Financial') # AND ??
        PERSONAL = 'personal', _('Personal')
        IT = 'info_techno', _('Info_techno')


    accounts = models.ManyToManyField(
        Account,
        related_name='questionnaires',
        blank=True,
        verbose_name=_("Assigned Accounts"),
        help_text=_("Accounts that can access this questionnaire.")
    )
    name = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name=_("Name"),
        help_text=_("Unique identifier for the questionnaire (e.g., 'KYC Form 2023').")
    )
    version = models.CharField(
        max_length=20,
        db_index=True,
        default='1.0',
        verbose_name=_("Version"),
        help_text=_("Semantic version (e.g., 1.2.3) for tracking changes.")
    )
    category = models.CharField(
        max_length=50,
        choices=Category.choices,
        verbose_name=_("Category"),
        help_text=_("Classification of questionnaire content.")
    )
    supported_languages = models.JSONField(
        default=list,
        verbose_name=_("Supported Languages"),
        help_text=_("List of language codes (e.g., ['en', 'es']) for multilingual support.")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("Purpose and instructions for respondents.")
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name=_("Status"),
        help_text=_("Publication state of the questionnaire.")
    )
    is_required = models.BooleanField(
        default=False,
        verbose_name=_("Is Required"),
        help_text=_("Whether completion is mandatory for assigned accounts.")
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name=_("Publicly Available"),
        help_text=_("Allows clients to complete this questionnaire voluntarily.")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("When this questionnaire version was created.")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
        help_text=_("Last modification timestamp.")
    )


    class Meta:
        verbose_name = _("Questionnaire")
        verbose_name_plural = _("Questionnaires")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name', 'status'])  # Composite index
        ]
        permissions = [
            ("can_publish_questionnaire", "Can publish questionnaire"),
            ("can_assign_questionnaire", "Can assign questionnaire to accounts"),
        ]


    def __str__(self):
        return f"{self.name} v{self.version})"


class Question(BaseModel):
    """
    Represents an individual question item that can be reused across multiple questionnaires.
    Supports various response types and validation rules.
    """

    class Type(models.TextChoices):
        TEXT = 'text', _('Text Input')
        MULTIPLE_CHOICE = 'multiple_choice', _('Multiple Choice') # ???
        FILE_UPLOAD = 'file', _('File Upload')
        DATE = 'date', _('Date Selector')

    questionnaires = models.ManyToManyField(
        Questionnaire,
        related_name='questions',
        verbose_name=_("Questionnaires"),
        help_text=_("Forms where this question appears.")
    )
    reference_code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name=_("Reference Code"),
        help_text=_("Unique identifier for business logic (e.g., 'TAX_ID_VERIFICATION').")
    )
    text = models.JSONField(
        verbose_name=_("Question Text"),
        help_text=_("Multilingual question content (e.g., {'en': 'Your name?', 'es': '¿Su nombre?'}).")
    )
    type = models.CharField(
        max_length=50,
        choices=Type.choices,
        default=Type.TEXT,
        db_index=True,
        verbose_name=_("Response Type"),
        help_text=_("Determines what input widget to display.")
    )
    validation_rules = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Validation Rules"),
        help_text=_("Configurable validation (e.g., {'min_length': 2, 'max_length': 100}).")
    )
    is_required = models.BooleanField(
        default=True,
        verbose_name=_("Is Required"),
        help_text=_("Whether this question must be answered.")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("When this question was first defined.")
    )


    class Meta:
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")
        ordering = ['-reference_code']
        indexes = [
            models.Index(fields=['reference_code', 'type']),
        ]


    def __str__(self):
        # Safely access the first available translation
        if isinstance(self.text, dict) and self.text:
            first_text = next(iter(self.text.values()), 'Untitled Question')
            return f"{self.reference_code}: {str(first_text)[:50]}"
        return f"{self.reference_code}: (No text defined)"
