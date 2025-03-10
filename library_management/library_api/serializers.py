from rest_framework import serializers
from models import User
from django.contrib.auth.hashers import make_password

class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model= User
        fields = ['id', 'name', 'email', 'user_id', 'department', 'identification', 'password']
        extra_kwargs = {'pasword': {'write_only': True}}
    
    def create(self, validated_data):
        # Hash the password before creating the user
        validated_data['password'] = make_password(validated_data['password'])
        user = User.objects.create(**validated_data)
        return user