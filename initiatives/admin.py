from django.contrib import admin
from .models import Initiative, Category, Company

@admin.register(Initiative)
class InitiativeAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'current_amount', 'goal_amount', 'duration_months', 'project_scale', 'location', 'technology_type')
    list_filter = ('status', 'category', 'location', 'technology_type')

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'status', 'total_shares', 'shares_sold', 'share_price', 'duration_months', 'company_scale', 'location', 'technology_type')
    list_filter = ('status', 'category', 'location', 'technology_type')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)