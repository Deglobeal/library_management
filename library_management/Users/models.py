from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class BaseUser(AbstractUser):   # User base model for all users
    user_id = models.CharField(max_length=10, unique=True, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=11, unique=True)
    address = models.TextField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone']
    
    class Meta:
        abstract = True # not to create a table for this model
        
    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = self.generate_user_id() # generate user_id
        
    def __str__(self):
        return f"{self.username} - {self.email} - {self.user_id}"
    
    # student model will inherit this model and will have a user_id field
    # user_id will be generated automatically when a student is created 
class Student(BaseUser):  # Student model
    roll = models.CharField(max_length=10, unique=True)
    department = models.CharField(max_length=50)
    session = models.CharField(max_length=10)
    
    def __str__(self):
        return f"{self.username} - {self.roll} - {self.department} - {self.session}"
    
    REQUIRED_FIELDS = BaseUser.REQUIRED_FIELDS + ['roll', 'department', 'session']

# generate user_id for all users    
    
    def save(self, *args, **kwargs): # override save method
        if not self.user_id: 
            self.user_id = self.generate_user_id() # generate user_id
        super().save(*args, **kwargs) #
        
    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
    
        
#  model for librarian

class Libraraian( BaseUser):
    staff_id = models.CharField(max_length=10, unique=True)
    is_approved = models.BooleanField(default=False)
    
    
    def save(self,  *args, **kwargs):
        if not self.staff_id:
            self.staff_id = self.generate_staff_id()
        super().save(*args, **kwargs)
        
        def generate_staff_id(self):
            # Implement your logic to generate a unique staff ID
            return f"STF{self.pk:05d}" # generate staff_id
        class Meta:
            verbose_name = 'Librarian'
            verbose_name_plural = 'Librarians'
            
               