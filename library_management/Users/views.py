from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from .models import Student, Librarian
from rest_framework.generics import RetrieveAPIView, ListAPIView
from .serializers import StudentSerializer, LibrarianSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser

# Create your views here.

class StudentView(viewsets.ModelViewSet): # viewset for student
    queryset = Student.objects.all() 
    serializer_class = StudentSerializer 
    permission_classes = [permissions.IsAuthenticated]

class LibrarianViewSet(viewsets.ModelViewSet):
    queryset = Librarian.objects.all()
    serializer_class = LibrarianSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    

