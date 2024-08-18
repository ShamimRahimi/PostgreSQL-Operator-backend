from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class App(models.Model):
    name = models.CharField(max_length=255)
    creation_time = models.DateTimeField(auto_now_add=True)
    STATE_CHOICES = [
        ('starting', 'Starting'),
        ('running', 'Running'),
        ('error', 'Error'),
        ('offline', 'Offline'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    state = models.CharField(max_length=10, choices=STATE_CHOICES, default='offline')
    size = models.PositiveIntegerField()

    def __str__(self):
        return self.name
    


