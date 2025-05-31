from django.db import models

class Usuario(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)