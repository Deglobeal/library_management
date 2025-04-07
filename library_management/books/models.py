from django.db import models
from Users.models import User
from django.conf import settings

# Create your models here.
class Book(models.Model):
    
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    
    
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    genre = models.CharField(max_length=50)     
    publication_date = models.DateField()
    isbn = models.CharField(max_length=13, unique=True)
    copies_available = models.IntegerField(default=0)
    picture = models.ImageField(
        upload_to='book_covers/',
        null=True,
        blank=True,
        default='book_covers/default.jpg'
    )
    added_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True,
        limit_choices_to = {'user_type': 'librarian'},
        related_name='added_books')
    
    date_added = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    
    currently_borrowed = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='transactions.Transaction',
        related_name='borrowed_books',
        blank=True
    )

    def __str__(self):
        return f"{self.title} by {self.author}"