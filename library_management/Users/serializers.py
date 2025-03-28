from rest_framework import serializers
from .models import Student, Librarian, User

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'phone']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            phone=validated_data['phone'],
            user_type=self.context.get('user_type', 'student')
        )
        return user

class StudentSerializer(serializers.ModelSerializer):
    user = UserRegistrationSerializer()
    roll = serializers.CharField()
    department = serializers.CharField()
    session = serializers.CharField()

    class Meta:
        model = Student
        fields = ['user', 'roll', 'department', 'session']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = UserRegistrationSerializer(data=user_data)
        
        if user_serializer.is_valid():
            user = user_serializer.save(user_type='student')
            return Student.objects.create(
                user=user,
                **validated_data
            )
        raise serializers.ValidationError(user_serializer.errors)
class LibrarianSerializer(serializers.ModelSerializer):
    user = UserRegistrationSerializer()
    staff_id = serializers.CharField()

    class Meta:
        model = Librarian
        fields = ['user', 'staff_id']
        read_only_fields = ['is_approved']

    class Meta:
        model = Librarian
        fields = ['user', 'staff_id']
        read_only_fields = ['is_approved']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = UserRegistrationSerializer(data=user_data, context={'user_type': 'librarian'})  # Fix: Use context
        if user_serializer.is_valid():
            user = user_serializer.save()  # Fix: Use serializer to create user
            return Librarian.objects.create(
                user=user,
                staff_id=validated_data['staff_id']
            )
        raise serializers.ValidationError(user_serializer.errors)  # Propagate errors