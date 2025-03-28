from django.db import models

# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    genre = models.CharField(max_length=50)     
    publication_date = models.DateField()
    isbn = models.CharField(max_length=13, unique=True)
    copies_available = models.IntegerField(default=0)

    def __str__(self):
        return self.title