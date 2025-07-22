# Built-in
from __future__ import annotations
from typing import TYPE_CHECKING

# External
from django.db.models import QuerySet

# Internal
from ..repo import QuestionnaireRepository

if TYPE_CHECKING:
    from typing import Any, Dict, Optional, Tuple
    from ..models import Questionnaire


class QuestionnaireService:
    """
    Encapsulates business logic for Questionnaire entities.
    """

    @staticmethod
    def list_questionnaires(status: Optional[str] = None) -> Tuple[int, QuerySet[Questionnaire]]:
        """
        Retrieve questionnaires, optionally filtering by status.

        :param status: Optional status to filter by (e.g., 'draft', 'public', 'private').
        :return: A tuple of (total_count, queryset) where:
                 - total_count is the number of matched questionnaires.
                 - queryset is a Django QuerySet of Questionnaire instances.
        """
        q_repo = QuestionnaireRepository()

        if status:
            queryset: QuerySet[Questionnaire] = q_repo.manager.filter_by(status=status)
        else:
            queryset: QuerySet[Questionnaire] = q_repo.manager.get_all()

        total: int = queryset.count()
        return total, queryset


    @staticmethod
    def create_questionnaire(data: Dict[str, Any]) -> Questionnaire:
        """
        Create and persist a new Questionnaire from validated data.

        :param data: Dict of fields matching Questionnaire model.
        :return: The newly created Questionnaire instance.
        """
        repo = QuestionnaireRepository()
        instance = repo.manager.create_instance(**data)
        return instance

