from django.db import models
from django.core.validators import MinValueValidator
from investments.portfolio_analyzer import PortfolioAnalyzer

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, choices=[
        ('Renewable Energy', 'Renewable Energy'),
        ('Recycling', 'Recycling'),
        ('Emission Control', 'Emission Control'),
        ('Water Conservation', 'Water Conservation'),
        ('Reforestation', 'Reforestation'),
        ('Sustainable Agriculture', 'Sustainable Agriculture'),
        ('Clean Transportation', 'Clean Transportation'),
        ('Waste Management', 'Waste Management'),
        ('Green Technology', 'Green Technology'),
        ('Ocean Conservation', 'Ocean Conservation'),
    ])
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Initiative(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('funded', 'Funded'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]
    LOCATION_CHOICES = [
        ('North India', 'North India'),
        ('South India', 'South India'),
        ('East India', 'East India'),
        ('West India', 'West India'),
    ]
    TECHNOLOGY_CHOICES = [
        ('Solar', 'Solar'),
        ('Wind', 'Wind'),
        ('Hydro', 'Hydro'),
        ('Organic', 'Organic'),
        ('Mechanical', 'Mechanical'),
        ('Chemical', 'Chemical'),
        ('Biofuel', 'Biofuel'),
        ('EV', 'EV'),
        ('Manual', 'Manual'),
        ('AI', 'AI')
    ]
    RISK_CHOICES = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk')
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    categories = models.ManyToManyField(Category, related_name='initiatives')
    image = models.ImageField(upload_to='initiatives/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    location = models.CharField(max_length=100)
    technology_type = models.CharField(max_length=20, choices=TECHNOLOGY_CHOICES, default='Manual')
    goal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    risk_level = models.CharField(max_length=20, choices=RISK_CHOICES, default='medium')
    duration_months = models.IntegerField(default=12)
    min_investment = models.DecimalField(max_digits=10, decimal_places=2, default=1000)
    max_investment = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    roi_estimate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    carbon_reduction_per_investment = models.FloatField(default=0)
    energy_savings_per_investment = models.FloatField(default=0)
    water_savings_per_investment = models.FloatField(default=0)
    carbon_impact = models.FloatField(default=0)  # CO2 reduction in kg
    energy_impact = models.FloatField(default=0)  # Energy saved in kWh
    water_impact = models.FloatField(default=0)   # Water saved in liters
    project_scale = models.IntegerField(
        choices=[
            (1, 'Small'),
            (2, 'Medium'),
            (3, 'Large'),
            (4, 'Very Large'),
            (5, 'Enterprise')
        ],
        default=3
    )

    def __str__(self):
        return self.title

    def calculate_risk_score(self):
        analyzer = PortfolioAnalyzer()
        return analyzer.calculate_risk_score(self)
    
    def get_risk_label(self):
        analyzer = PortfolioAnalyzer()
        return analyzer.get_risk_label(self.calculate_risk_score())

    def get_progress_percentage(self):
        if self.goal_amount == 0:
            return 0
        return (self.current_amount / self.goal_amount) * 100

    class Meta:
        ordering = ['-created_at']