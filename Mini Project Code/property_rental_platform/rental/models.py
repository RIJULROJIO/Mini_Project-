from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Add custom fields here if needed
    role = models.CharField(max_length=15)  # For custom user roles, if needed

    def __str__(self):
        return self.username  # You can use any field for representation

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
