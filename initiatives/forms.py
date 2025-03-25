from django import forms
from .models import Initiative, Category

class InitiativeForm(forms.ModelForm):
    class Meta:
        model = Initiative
        fields = [
            'title', 'description', 'image', 'categories', 'location',
            'goal_amount', 'min_investment', 'max_investment',
            'project_scale', 'duration_months'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'categories': forms.CheckboxSelectMultiple(),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field in self.fields.values():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            elif isinstance(field.widget, forms.NumberInput):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.update({'class': 'form-check'}) 