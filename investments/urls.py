from django.urls import path
from . import views

urlpatterns = [
    path('invest/<int:initiative_id>/', views.invest, name='invest'),
]