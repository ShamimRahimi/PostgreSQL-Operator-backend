from django.db import models
from django.utils import timezone
from datetime import timedelta
from uuid import uuid4
from django.contrib.auth.models import User


# Create your models here.
class Token(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=255, unique=True)
    expiration_time = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expiration_time
    
    @classmethod
    def generate_token(cls, user):
        key = uuid4()
        expiration_time = timezone.now() + timedelta(hours=1)
        token = Token(user=user, key=key, expiration_time=expiration_time)
        token.save()
        return token