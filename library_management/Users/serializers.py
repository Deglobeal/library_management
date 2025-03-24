from .models import Librarian, Student
from rest_framework import serializers



class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
        
from rest_framework import serializers
class LibrarianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Librarian
        fields = '__all__'