from django.urls import path
from . import views

urlpatterns = [
    path('invest/<int:initiative_id>/', views.invest_initiative, name='invest_initiative'),
    path('invest_company/<int:company_id>/', views.invest_company, name='invest_company'),
]