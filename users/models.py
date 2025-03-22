from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)

    def __str__(self):
        return self.username

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    carbon_reduced = models.FloatField(default=0.0)
    energy_saved = models.FloatField(default=0.0)
    water_conserved = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.user.username}'s Profile"