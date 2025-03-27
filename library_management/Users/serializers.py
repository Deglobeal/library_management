from rest_framework import serializers
from .models import Student, Librarian, User

# Serializers define the API representation.
# Here we are defining the serializers for Student and Librarian models.
class StudentSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    user_id = serializers.CharField(read_only=True)

    class Meta:
        model = Student
        fields = ['user_id', 'email', 'username', 'password', 'phone', 'roll', 'department', 'session']

    def create(self, validated_data):
        user = Student.objects.create(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            phone=validated_data['phone'],
            roll=validated_data['roll'],
            department=validated_data['department'],
            session=validated_data['session'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

# Librarian serializer
# This is the serializer for the Librarian model. It is used to serialize the data of the Librarian model for API responses.
class LibrarianSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Librarian
        fields = ['email', 'username', 'password', 'phone']
        read_only_fields = ['is_approved']
        
        
    def create(self, validated_data):
        user_data = {
            'email': validated_data['email'],
            'username': validated_data['username'],
            'phone': validated_data['phone'],
            'password': validated_data['password'],
            'user_type': 'librarian',
        }
        user = User.objects.create_user(**user_data)
        user.set_password(validated_data['password'])
        user.save()
    
# Admin serializer
# This is the serializer for the Admin model. It is used to serialize the data of the Admin model for API responses.
class AdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'phone']

    def create(self, validated_data):
        user = User.objects.create_superuser(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            phone=validated_data['phone'],
            user_type='admin'
        )
        return user