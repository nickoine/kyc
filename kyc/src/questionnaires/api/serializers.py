# External
from django.db.models import QuerySet
from rest_framework import serializers


# Internal
from typing import Any, Dict, Tuple
from .. import Questionnaire
from ....common.base_view import BaseReadSerializer, BaseWriteSerializer
from ..service.qnnaire import QuestionnaireService


class QuestionnaireForAdminSerializer(BaseReadSerializer):
    """
    Serializer for reading Questionnaire data in admin views.
    """
    question_count = serializers.IntegerField(source='items.count', read_only=True)

    class Meta:
        model = Questionnaire
        fields = [
            'id', 'name', 'description', 'type', 'status', 'group',
            'created_by', 'created_at', 'updated_at', 'question_count',
        ]
        read_only_fields = [
            'id', 'created_by', 'created_at', 'updated_at', 'question_count',
        ]

    def represent(self, instance: Any) -> Dict[str, Any]:
        pass


    @classmethod
    def list(cls, data: Dict[str, Any]) -> Tuple[int, QuerySet]:
        """
        Delegate to the domain service to fetch filtered questionnaires.
        """
        service = QuestionnaireService()
        return service.list_questionnaires(status=data.get("status"))


class QuestionnaireCreateByAdminSerializer(BaseWriteSerializer):
    """
    Serializer for admin to create new Questionnaires.
    """
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=1000, allow_blank=True)
    type = serializers.ChoiceField(choices=Questionnaire.TYPE_CHOICES)
    status = serializers.ChoiceField(choices=Questionnaire.STATUS_CHOICES)
    group = serializers.CharField(max_length=255)
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    def create(self, data: Dict[str, Any]) -> Questionnaire:
        return QuestionnaireService().create_questionnaire(data)