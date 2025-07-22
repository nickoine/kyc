# from __future__ import annotations
# from abc import ABC, abstractmethod
# from django.db.models import QuerySet
#
# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     from typing import Any, Dict, Tuple
#     from rest_framework import serializers
#
#
# class BaseViewService(ABC):
#     """
#     Base class for view services to handle request orchestration.
#     """
#     class Meta:
#         abstract = True
#
#     @abstractmethod
#     def handle_create(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
#         ...
#
#
#     @abstractmethod
#     def handle_list(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
#         ...
#
#
# class BaseReadSerializer(serializers.ModelSerializer, ABC):
#     """
#     Abstract base for serializers with a set of fields based on the model.
#     Provides common configurations and utility methods.
#     """
#     class Meta:
#         abstract = True
#
#     @abstractmethod
#     def represent(self, instance: Any) -> Dict[str, Any]:
#         """Enforce implementation of representation logic."""
#         ...
#
#
#     @classmethod
#     @abstractmethod
#     def list(cls, data: Dict[str, Any]) -> Tuple[int, QuerySet]:
#         """
#         Must be overridden by subclasses to return (count, queryset)
#         """
#         raise NotImplementedError("Subclasses must implement .list()")
#
#
# class BaseWriteSerializer(serializers.Serializer, ABC):
#     """
#     Abstract base for serializers.
#     Provides common configurations and utility methods.
#     """
#     class Meta:
#         abstract = True
#
#     @abstractmethod
#     def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
#         ...