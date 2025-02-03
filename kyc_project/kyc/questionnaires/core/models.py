# Internal
from ... import Account

# External
from django.db import models


class Questionnaire(models.Model):

    questionnaire_accounts = models.ManyToManyField(Account, related_name='questionnaires')  # Accounts associated with the questionnaire
    questionnaire_name = models.CharField(max_length=255)  # Name of the questionnaire
    questionnaire_type = models.CharField(max_length=50)  # Type of questionnaire
    questionnaire_category = models.CharField(max_length=50)  # Category of questionnaire
    questionnaire_language = models.JSONField(default=list)  # List of supported languages
    questionnaire_description = models.TextField()  # Description of the questionnaire
    questionnaire_status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('archived', 'Archived')
    ], default='active')  # Status of the questionnaire
    questionnaire_created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for creation
    questionnaire_deleted_at = models.DateTimeField(null=True, blank=True)  # Timestamp for deletion (optional)

    def __str__(self):
        return self.questionnaire_name

# Question Table
class Question(models.Model):

    question_questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)  # Links question to a questionnaire
    question_name = models.CharField(max_length=255)  # Question text
    question_description = models.TextField()  # Detailed description of the question
    question_type = models.CharField(max_length=50)  # Type of question (e.g., text, multiple-choice)
    question_created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for question creation

    def __str__(self):
        return self.question_name

# Responses Table
class UserResponse(models.Model):

    response_account = models.ForeignKey(Account, on_delete=models.CASCADE)  # Links response to an account
    response_questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)  # Links response to a questionnaire
    response_question = models.ForeignKey(Question, on_delete=models.CASCADE)  # Links response to a question
    response_data = models.JSONField()  # Stores the response data as structured JSON
    response_submitted_at = models.DateTimeField(auto_now_add=True)  # Timestamp for response submission

    def __str__(self) -> str:
        return (f"Response is {self.response_data}. By Account {self.response_account}"
                f" on {self.response_question} from {self.response_questionnaire} .")
