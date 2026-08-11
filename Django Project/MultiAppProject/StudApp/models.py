from django.db import models

# Create your models here.
class StudInfo(models.Model):
    name=models.CharField(max_length=20)
    email=models.EmailField()
    subject=models.CharField(max_length=20)
