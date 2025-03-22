from django.contrib import admin
from .models import Category, Initiative

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Initiative)
class InitiativeAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'current_amount', 'goal_amount')
    list_filter = ('status', 'category')