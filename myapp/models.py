from django.db import models

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
    state = models.CharField(max_length=10, choices=STATE_CHOICES, default='offline')
    size = models.PositiveIntegerField()

    def __str__(self):
        return self.name