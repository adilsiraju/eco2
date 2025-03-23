from django.db import models
from django.conf import settings
from initiatives.models import Initiative, Company

class Investment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='investments')
    initiative = models.ForeignKey(Initiative, on_delete=models.CASCADE, null=True, blank=True, related_name='investments')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, related_name='investments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    shares_purchased = models.PositiveIntegerField(default=0, help_text="Number of shares bought (for companies)")
    carbon_reduced = models.FloatField(default=0.0)
    energy_saved = models.FloatField(default=0.0)
    water_conserved = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.initiative:
            return f"{self.user.username} - {self.initiative.title} - ₹{self.amount}"
        elif self.company:
            return f"{self.user.username} - {self.company.name} - {self.shares_purchased} shares (₹{self.amount})"
        return f"{self.user.username} - Unknown Investment - ₹{self.amount}"