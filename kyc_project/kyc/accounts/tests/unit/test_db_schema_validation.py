# from typing import TYPE_CHECKING
#
# from django.test import TestCase
# from django.apps import apps
# from django.db import connection
#
# if TYPE_CHECKING:
#     from typing import Dict, Set, Any
#
# class TestDatabaseEntity(TestCase):
#
#     @classmethod
#     def setup(cls):
#         """
#         Fetch all relevant database metadata before running tests to improve efficiency.
#         """
#         super().setUpClass()
#         cls.expected_tables = {model._meta.db_table for model in apps.get_models()}
#         cls.existing_tables = cls.get_existing_tables()
#         cls.model_columns = cls.get_model_columns()
#         cls.database_columns = cls.get_database_columns()
#         cls.model_indexes = cls.get_model_indexes()
#         cls.database_indexes = cls.get_database_indexes()
#
#     @staticmethod
#     def get_existing_tables() -> Set:
#         """
#         Fetch all table names.
#         """
#         with connection.cursor() as cursor:
#             cursor.execute(
#                 "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
#             )
#             return {row[0] for row in cursor.fetchall()}
#
#     @staticmethod
#     def get_database_columns() -> Dict[Any, Set]:
#         """
#         Fetch all columns for each table.
#         """
#         columns = {}
#         with connection.cursor() as cursor:
#             cursor.execute(
#                 "SELECT table_name, column_name FROM information_schema.columns WHERE table_schema = 'public';"
#             )
#             for table, column in cursor.fetchall():
#                 columns.setdefault(table, set()).add(column)
#         return columns
#
#     @staticmethod
#     def get_database_indexes() -> Dict[Any, Set]:
#         """
#         Fetch all indexes for each table.
#         """
#         indexes = {}
#         with connection.cursor() as cursor:
#             cursor.execute(
#                 "SELECT tablename, indexname FROM pg_indexes WHERE schemaname = 'public';"
#             )
#             for table, index in cursor.fetchall():
#                 indexes.setdefault(table, set()).add(index)
#         return indexes
#
#     @staticmethod
#     def get_model_columns() -> Dict[Any, Set]:
#         """
#         Retrieve expected columns.
#         """
#         return {
#             model._meta.db_table: {field.column for field in model._meta.fields}
#             for model in apps.get_models()
#         }
#
#     @staticmethod
#     def get_model_indexes() -> Dict[Any, Set]:
#         """
#         Retrieve expected indexes.
#         """
#         model_indexes = {}
#         for model in apps.get_models():
#             table_name = model._meta.db_table
#             unique_fields = {
#                 constraint.name for constraint in model._meta.constraints if constraint.name
#             }
#             model_indexes[table_name] = unique_fields
#         return model_indexes
#
#     def test_database_tables_exist(self) -> None:
#         """
#         Ensure all expected database tables for models exist.
#         """
#         missing_tables = self.expected_tables - self.existing_tables
#         unexpected_tables = self.existing_tables - self.expected_tables
#
#         self.assertFalse(
#             missing_tables,
#             f"Missing tables in the database: {missing_tables}"
#         )
#         self.assertFalse(
#             unexpected_tables,
#             f"Unexpected tables found in the database: {unexpected_tables}"
#         )
#
#     def test_table_columns_match_model_fields(self) -> None:
#         """
#         Ensure all database tables have the expected columns based on model definitions.
#         """
#         for table, expected_columns in self.model_columns.items():
#             actual_columns = self.database_columns.get(table, set())
#
#             missing_columns = expected_columns - actual_columns
#             extra_columns = actual_columns - expected_columns
#
#             self.assertFalse(
#                 missing_columns or extra_columns,
#                 f"Column mismatch in '{table}'. Missing: {missing_columns}, Extra: {extra_columns}"
#             )
#
#     def test_table_indexes_match_model_design(self) -> None:
#         """
#         Ensure all database tables have the expected indexes based on model design.
#         """
#         for table, expected_indexes in self.model_indexes.items():
#             actual_indexes = self.database_indexes.get(table, set())
#
#             missing_indexes = expected_indexes - actual_indexes
#             extra_indexes = actual_indexes - expected_indexes
#
#             self.assertFalse(
#                 missing_indexes or extra_indexes,
#                 f"Index mismatch in '{table}'. Missing: {missing_indexes}, Extra: {extra_indexes}"
#             )
def test_one():
    print("-----------------------TEST HAS FINISHED!---------------------------")