from django.urls import path
from .views import AdminQuestionnaireListCreateView, QuestionnaireDetailView

urlpatterns = [
    path('', AdminQuestionnaireListCreateView.as_view(), name='admin-ques-list-create'),
    path('<int:pk>/', QuestionnaireDetailView.as_view(), name='admin-ques-detail'),
]
