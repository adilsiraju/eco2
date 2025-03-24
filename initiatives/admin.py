from django.contrib import admin
from .models import Initiative, Category

@admin.register(Initiative)
class InitiativeAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'current_amount', 'goal_amount', 'duration_months', 'project_scale', 'location', 'technology_type')
    list_filter = ('status', 'categories', 'location', 'technology_type')
    filter_horizontal = ('categories',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)