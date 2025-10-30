from django.db import models

# Create your models here

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pin = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_valid(self):
        """Check if the PIN is still valid."""
        return timezone.now() < self.expires_at

    def __str__(self):
        return f"{self.user.email} - {self.pin}"