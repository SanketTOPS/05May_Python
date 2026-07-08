from django.db import models

# Create your models here.

class Userinfo(models.Model):
    name=models.CharField(max_length=20)
    email=models.EmailField()
    mobile=models.BigIntegerField()
    dob=models.DateField()
    
    def __str__(self):
        return self.name
    
    
