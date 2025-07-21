# External
from __future__ import annotations
from rest_framework import serializers, status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

# Internal
from kyc.common.base_view import BaseViewService
from ..api.serializers import QuestionnaireForAdminSerializer, QuestionnaireCreateByAdminSerializer

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Dict, Any, Type, Optional
    from kyc.common.base_view import BaseReadSerializer, BaseWriteSerializer
    from kyc.src.questionnaires.models import Questionnaire


class AdminQuestionnaireViewService(BaseViewService):
    """
    View-service orchestrating validation and execution steps for admin questionnaire endpoint.
    """
    read_serializer: Type[BaseReadSerializer] = QuestionnaireForAdminSerializer
    write_serializer: Type[BaseWriteSerializer] = QuestionnaireCreateByAdminSerializer


    def handle_create(self, processed_data: Dict[str, Any]) -> Response:
        """
        POST → delegate the operation to the write_serializer, then read_serialize results.
        """

        try:
            write_ser = self.write_serializer(data=processed_data, context=getattr(self, 'context', {}))
            write_ser.is_valid(raise_exception=True) # needs a serializer instance in order to call .save()
            instance: Questionnaire = write_ser.save()
            read_ser = self.read_serializer(instance, context={"request": None})
            return Response(read_ser.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({"detail": e.detail}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

        except NotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)


    def handle_list(self, processed_data: Dict[str, Any]) -> Response:
        """
        GET → delegate the operation to the read_serializer.
        """

        try:
            count, queryset = self.read_serializer.list(data=processed_data)
            serialized = self.read_serializer(queryset, many=True, context=getattr(self, 'context', {}))
            return Response({"count": count, "results": serialized.data}, status=status.HTTP_200_OK)

        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

        except NotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


    def validate(self, request: Request) -> Dict[str, Any] | QuestionnaireCreateByAdminSerializer:
        """
        Extract and validate inputs based on HTTP method.
        """

        if request.method == "GET":
            status_param: Optional[str] = request.query_params.get("status")
            # validate against allowed statuses
            allowed = {c[0] for c in Questionnaire.STATUS_CHOICES}
            if status_param and status_param not in allowed:
                raise serializers.ValidationError({"status": "Invalid status filter"})
            return {"status": status_param}

        # POST
        serializer = self.write_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return serializer


    @staticmethod
    def normalize(data: Dict[str, Any], method: str, *, request: Optional[Request] = None) -> Dict[str, Any]:
        """
        Optional transformation/enrichment.
        - GET: normalize the status filter.
        - POST: normalize enum fields and inject the acting user.
        """
        if method == "GET":
            if status_val := data.get("status"):
                data["status"] = status_val.lower()

        elif method == "POST":
            # normalize enum fields
            for field in ("type", "status"):
                if val := data.get(field):
                    data[field] = val.lower()

            # trim whitespace on name/description
            if name := data.get("name"):
                data["name"] = name.strip()
            if desc := data.get("description"):
                data["description"] = desc.strip()

            # inject the admin user as creator, if not already set
            if request and "created_by" not in data:
                data["created_by"] = request.user

        return data

