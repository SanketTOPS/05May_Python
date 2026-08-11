from rest_framework import serializers
from .models import *

class UserSerial(serializers.ModelSerializer):
    class Meta:
        model=Userinfo
        fields='__all__'