from django.urls.conf import path, include
from qanda import views
from .views import QuestionAPI, latest
from rest_framework import routers

router = routers.DefaultRouter()
router.register("questions", QuestionAPI)

app_name = 'qanda'

urlpatterns = [
            path('ask', views.AskQuestionView.as_view(), name='ask'),
            path('question/<int:pk>', views.QuestionDetailView.as_view(),name='question_detail'),
            path('question/<int:pk>/answer', views.CreateAnswerView.as_view(),name='answer_question'),
            path('question/<int:pk>/accept', views.UpdateAnswerAcceptanceView.as_view(),name='update_answer_acceptance'),
            path('daily/<int:year>/<int:month>/<int:day>/', views.DailyQuestionList.as_view(), name='daily_questions'),
            path('', views.TodaysQuestionList.as_view(), name='index'),
            path('', include(router.urls)),
            path('scrap', latest, name="latest"),
            ]


