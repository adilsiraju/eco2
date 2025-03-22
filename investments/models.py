from django.db import models
from users.models import CustomUser
from initiatives.models import Initiative

class Investment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='investments')
    initiative = models.ForeignKey(Initiative, on_delete=models.CASCADE, related_name='investments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    carbon_reduced = models.FloatField(default=0.0)
    energy_saved = models.FloatField(default=0.0)
    water_conserved = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} invested {self.amount} in {self.initiative.title}"