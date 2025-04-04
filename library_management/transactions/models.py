from django.db import models
from django.utils import timezone
from Users.models import Student
from django.contrib.auth.models import User
from books.models import Book

class Transaction(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='transactions')
    borrower = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='borrowed_books')
    borrow_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    fine = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        is_new = not self.pk
        if is_new:
            self.book.copies_available -= 1
            self.book.save()
        elif self.return_date:
            original = Transaction.objects.get(pk=self.pk)
            if not original.return_date:
                self.book.copies_available += 1
                self.book.save()
        super().save(*args, **kwargs)

    def calculate_fine(self):
        if self.return_date and self.return_date > self.due_date:
            overdue_days = (self.return_date - self.due_date).days
            self.fine = overdue_days * 1  # $10 per day fine
            self.save()
        return self.fine

    def __str__(self):
        return f"{self.borrower.user.email} borrowed {self.book.title}"
            