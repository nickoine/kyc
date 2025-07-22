# Built-in
from typing import Optional

# External
from rest_framework import serializers

# Internal
from .. import Questionnaire


class BaseQuestionnaireSerializer(serializers.ModelSerializer):

    class Meta:
        model = Questionnaire
        fields = ['id', 'name', 'description', 'type', 'status', 'group']
        read_only_fields = ['id']


class QuestionnaireForAdminSerializer(BaseQuestionnaireSerializer):

    question_count = serializers.IntegerField(source='questions.count', read_only=True)

    class Meta(BaseQuestionnaireSerializer.Meta):

        fields = BaseQuestionnaireSerializer.Meta.fields + [
            'created_by', 'created_at', 'updated_by', 'updated_at', 'question_count'
        ]
        read_only_fields = fields


class QuestionnaireFilterSerializer(serializers.Serializer):

    status: Optional[str] = serializers.ChoiceField(
        choices=Questionnaire.STATUS_CHOICES,
        required=False,
        help_text="Filter by questionnaire status"
    )


class QuestionnaireCreateByAdminSerializer(BaseQuestionnaireSerializer):

    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # inherits name, description, type, status, group

    class Meta(BaseQuestionnaireSerializer.Meta):

        fields = BaseQuestionnaireSerializer.Meta.fields + ['created_by']



# class QuestionnaireForAdminSerializer(BaseReadSerializer):
#     """
#     Serializer for reading Questionnaire data in admin views.
#     """
#     question_count = serializers.IntegerField(source='items.count', read_only=True)
#
#     class Meta:
#         model = Questionnaire
#         fields = [
#             'id', 'name', 'description', 'type', 'status', 'group',
#             'created_by', 'created_at', 'updated_at', 'question_count',
#         ]
#         read_only_fields = [
#             'id', 'created_by', 'created_at', 'updated_at', 'question_count',
#         ]
#
#     def represent(self, instance: Any) -> Dict[str, Any]:
#         pass
#
#
#     @classmethod
#     def list(cls, data: Dict[str, Any]) -> Tuple[int, QuerySet]:
#         """
#         Delegate to the domain service to fetch filtered questionnaires.
#         """
#         service = QuestionnaireService()
#         return service.list_questionnaires(status=data.get("status"))
#
#
# class QuestionnaireCreateByAdminSerializer(BaseWriteSerializer):
#     """
#     Serializer for admin to create new Questionnaires.
#     """
#     name = serializers.CharField(max_length=255)
#     description = serializers.CharField(max_length=1000, allow_blank=True)
#     type = serializers.ChoiceField(choices=Questionnaire.TYPE_CHOICES)
#     status = serializers.ChoiceField(choices=Questionnaire.STATUS_CHOICES)
#     group = serializers.CharField(max_length=255)
#     created_by = serializers.HiddenField(
#         default=serializers.CurrentUserDefault()
#     )
#
#     def create(self, data: Dict[str, Any]) -> Questionnaire:
#         return QuestionnaireService().create_questionnaire(data)
