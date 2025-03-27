from django.db import models
from django.contrib.auth.models import AbstractUser, Permission, Group




# Create your models here.
# Replace abstract BaseUser with concrete User model
class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('librarian', 'Librarian'),
    )
    
    user_id = models.CharField(max_length=10, primary_key=True, unique=True, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=11, unique=True)
    address = models.TextField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    is_approved = models.BooleanField(default=False)

    groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)



    def save(self, *args, **kwargs):
        if not self.user_id:
            from uuid import uuid4
            self.user_id = f"USR{uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} ({self.user_type})"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, to_field='user_id')
    roll = models.CharField(max_length=10, unique=True)
    department = models.CharField(max_length=50)
    session = models.CharField(max_length=10)

class Librarian(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, to_field='user_id')
    staff_id = models.CharField(max_length=10, unique=True)
    is_approved = models.BooleanField(default=False)
    
