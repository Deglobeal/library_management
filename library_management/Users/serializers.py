from rest_framework import serializers
from .models import Student, Librarian, User
# serializers.py
class StudentSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    user_id = serializers.CharField(read_only=True)

    class Meta:
        model = Student
        fields = ['user_id', 'email', 'username', 'password', 'phone', 'roll', 'department', 'session']

    def create(self, validated_data):
        # Create User 
        user = {
            'email': validated_data['email'],
            'username': validated_data['username'],
            'password': validated_data['password'],
            'phone': validated_data['phone'],
            'user_type': 'student',
        }
        user.set_password(validated_data['password'])
        user.save()

        # Create Student linked to the User
        student = Student.objects.create(
            user=user,
            roll=validated_data['roll'],
            department=validated_data['department'],
            session=validated_data['session'],
        )
        return student

class LibrarianSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Librarian
        fields = ['email', 'username', 'password', 'phone', 'staff_id']
        read_only_fields = ['is_approved']

    def create(self, validated_data):
        # Create User first
        user = {
            'email': validated_data['email'],
            'username': validated_data['username'],
            'password': validated_data['password'],
            'phone': validated_data['phone'],
            'user_type': 'librarian',
        }
        user.set_password(validated_data['password'])
        user.save()

        # Create Librarian linked to the User
        librarian = Librarian.objects.create(
            user=user,
            staff_id=validated_data['staff_id'],
        )
        return librarian