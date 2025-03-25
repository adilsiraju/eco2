from django.contrib import admin
from .models import Category, Initiative

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Initiative)
class InitiativeAdmin(admin.ModelAdmin):
    list_display = (
        'title', 
        'status', 
        'location', 
        'goal_amount', 
        'current_amount', 
        'project_scale',
        'risk_level',
        'duration_months'
    )
    list_filter = (
        'status', 
        'location', 
        'project_scale',
        'risk_level',
        'categories'
    )
    search_fields = ('title', 'description', 'location')
    filter_horizontal = ('categories',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'image', 'categories', 'location')
        }),
        ('Financial Details', {
            'fields': ('goal_amount', 'current_amount', 'min_investment', 'max_investment', 'roi_estimate')
        }),
        ('Impact Metrics', {
            'fields': ('carbon_impact', 'energy_impact', 'water_impact', 
                      'carbon_reduction_per_investment', 'energy_savings_per_investment', 
                      'water_savings_per_investment')
        }),
        ('Project Details', {
            'fields': ('project_scale', 'risk_level', 'duration_months')
        }),
        ('Status Information', {
            'fields': ('status', 'created_at', 'updated_at')
        }),
    )