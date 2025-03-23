from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, choices=[
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
        ('active', 'Active'),
        ('funded', 'Funded'),
        ('completed', 'Completed'),
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
        ('EV', 'Electric Vehicle'),
        ('Manual', 'Manual'),
        ('AI', 'Artificial Intelligence'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='initiatives')
    image = models.ImageField(upload_to='initiatives/', null=True, blank=True)
    goal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    duration_months = models.PositiveIntegerField(default=12)
    project_scale = models.PositiveIntegerField(default=1, help_text="Scale of project (1=small, 5=medium, 10=large)")
    location = models.CharField(max_length=50, choices=LOCATION_CHOICES, default='North India')
    technology_type = models.CharField(max_length=50, choices=TECHNOLOGY_CHOICES, default='Manual')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Company(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('funded', 'Funded'),
        ('closed', 'Closed'),
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
        ('EV', 'Electric Vehicle'),
        ('Manual', 'Manual'),
        ('AI', 'Artificial Intelligence'),
    ]
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='companies')
    image = models.ImageField(upload_to='companies/', null=True, blank=True)
    total_shares = models.PositiveIntegerField(default=1000, help_text="Total shares available for purchase")
    shares_sold = models.PositiveIntegerField(default=0, help_text="Number of shares purchased")
    share_price = models.DecimalField(max_digits=10, decimal_places=2, default=100.00, help_text="Price per share in ₹")
    duration_months = models.PositiveIntegerField(default=12)
    company_scale = models.PositiveIntegerField(default=1, help_text="Scale of company (1=startup, 5=mid-size, 10=large)")
    location = models.CharField(max_length=50, choices=LOCATION_CHOICES, default='North India')
    technology_type = models.CharField(max_length=50, choices=TECHNOLOGY_CHOICES, default='Manual')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def total_value(self):
        return self.total_shares * self.share_price

    @property
    def current_value(self):
        return self.shares_sold * self.share_price

    @property
    def shares_remaining(self):
        return self.total_shares - self.shares_sold