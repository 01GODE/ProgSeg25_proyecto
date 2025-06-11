from django.db import models
from django.utils.timezone import now
import random

class Usuario(models.Model):
    class Meta:
        app_label = "proyecto"
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)

class LoginAttempt(models.Model):
    ip = models.GenericIPAddressField()  
    username = models.CharField(max_length=150)  
    attempts = models.PositiveIntegerField(default=0)  
    last_attempt = models.DateTimeField(auto_now=True)  
    
    def __str__(self):
        return f"{self.username} ({self.ip}) - {self.attempts} intentos"
    
class OTP(models.Model):
    user_id = models.IntegerField(null=True, blank=True)
    code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    #verificar si el codigo OTP ha expirado
    def is_expired(self):
        return (now() - self.created_at).total_seconds() > 300