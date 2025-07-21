# External
from typing import Any, Dict
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response

# Internal
from kyc.src.questionnaires.service.view_service import AdminQuestionnaireViewService


class AdminQuestionnaireListCreateView(GenericAPIView):
    """
    GET  /api/admin/questionnaires/       → list questionnaires (optional ?status=)
    POST /api/admin/questionnaires/       → create a new questionnaire
    """
    permission_classes = [IsAdminUser]
    view_service = AdminQuestionnaireViewService()

    def get(self, request: Request) -> Response:
        validated_data: Dict[str, Any] = self.view_service.validate(request)
        processed = self.view_service.normalize(data=validated_data, request=request, method=request.method)
        return self.view_service.handle_list(processed)


    def post(self, request: Request) -> Response:
        validated_data = self.view_service.validate(request)
        processed = self.view_service.normalize(data=validated_data, request=request, method=request.method)
        return self.view_service.handle_create(processed)




class QuestionnaireDetailView(GenericAPIView):
    pass