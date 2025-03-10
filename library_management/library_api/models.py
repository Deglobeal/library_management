from django.db import models

# Create your models here.
from django.db import models

class User(models.Model):
    STUDENT = 'student'
    STAFF = 'staff'
    ADMIN = 'admin'
    USER_TYPE_CHOICES = [
        (STUDENT, 'Student'),
        (STAFF, 'Staff'),
        (ADMIN, 'Admin'),
    ]

    # Define fields here
    name = models.CharField(max_length=100, blank=True) 
    email = models.CharField(unique=True, max_length=100) 
    user_id = models.CharField(max_length=10, unique=True, null=False)  
    department = models.CharField(max_length=100)
    identification = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default=STUDENT) 

    def __str__(self):
        return f"{self.name} ({self.user_id}) ({self.identification})"
