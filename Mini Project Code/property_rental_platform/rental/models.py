from django.db import models


# Create your models here.

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('tenant', 'Tenant'),
        ('owner', 'Property Owner'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='tenant')
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username
