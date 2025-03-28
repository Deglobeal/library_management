from django.db import models

# Create your models here.
class Books(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    publication_date = models.DateField()
    isbn_number = models.CharField(max_length=13, unique=True)
    genre = models.CharField(max_length=50)
    copies_available = models.IntegerField(default=0)

    def __str__(self):
        return self.title