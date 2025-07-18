# External
from __future__ import annotations

# Internal
from ...common import BaseRepository
from .models import Questionnaire, Question


class QuestionnaireRepository(BaseRepository[Questionnaire]):
    """Repository for handling Questionnaire model operations."""

    _model = Questionnaire


class QuestionRepository(BaseRepository[Question]):
    """Repository for handling Question model operations."""

    _model = Question