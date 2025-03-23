from django.urls import path
from . import views

urlpatterns = [
    path('', views.initiative_list, name='initiative_list'),
    path('<int:pk>/', views.initiative_detail, name='initiative_detail'),
    path('companies/', views.company_list, name='company_list'),
    path('companies/<int:pk>/', views.company_detail, name='company_detail'),
]