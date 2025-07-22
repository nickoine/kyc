# Built-in
from typing import TYPE_CHECKING, Any, Type, Optional

# External
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response


# Internal
from ..service.qnnaire import QuestionnaireService
from .serializers import (QuestionnaireForAdminSerializer,
                          QuestionnaireCreateByAdminSerializer,
                          QuestionnaireFilterSerializer)

if TYPE_CHECKING:
    from .serializers import BaseQuestionnaireSerializer
    from rest_framework.serializers import Serializer


class AdminQuestionnaireViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    GET  /api/admin/questionnaires/       → list (optional ?status=)
    POST /api/admin/questionnaires/       → create
    """
    permission_classes = [IsAdminUser]
    read_serializer: Type[BaseQuestionnaireSerializer] = QuestionnaireForAdminSerializer
    write_serializer: Type[BaseQuestionnaireSerializer] = QuestionnaireCreateByAdminSerializer


    def get_serializer_class(self) -> Type[Serializer]:
        return (
            self.read_serializer
            if self.action == "list"
            else self.write_serializer
        )

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        GET → delegate the operation to validator, then to Q service and return Response with serialized results.
        """
        filter_ser = QuestionnaireFilterSerializer(data=request.query_params)
        filter_ser.is_valid(raise_exception=True)
        status_filter: Optional[str] = request.query_params.get("status")
        total, qs = QuestionnaireService.list_questionnaires(status_filter)

        ser = self.get_serializer(qs, many=True)
        return Response({"count": total, "results": ser.data}, status=status.HTTP_200_OK)


    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        POST → delegate the operation to serializer, then to Q service and return Response with results.
        """
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)

        instance = QuestionnaireService.create_questionnaire(ser.validated_data)
        out_ser = self.get_serializer(
            instance, context=self.get_serializer_context()
        )
        return Response(out_ser.data, status=status.HTTP_201_CREATED)


# class AdminQuestionnaireListCreateView(GenericAPIView):
#     """
#     GET  /api/admin/questionnaires/       → list questionnaires (optional ?status=)
#     POST /api/admin/questionnaires/       → create a new questionnaire
#     """
#     permission_classes = [IsAdminUser]
#     view_service = AdminQuestionnaireViewService()
#
#     def get(self, request: Request) -> Response:
#         validated_data: Dict[str, Any] = self.view_service.validate(request)
#         processed = self.view_service.normalize(data=validated_data, request=request, method=request.method)
#         return self.view_service.handle_list(processed)
#
#
#     def post(self, request: Request) -> Response:
#         validated_data = self.view_service.validate(request)
#         processed = self.view_service.normalize(data=validated_data, request=request, method=request.method)
#         return self.view_service.handle_create(processed)
#
