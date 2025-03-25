from django.urls import path
from . import views

urlpatterns = [
    path('invest/<int:pk>/', views.invest_initiative, name='invest_initiative'),
    path('goals/add/', views.add_investment_goal, name='add_investment_goal'),
]