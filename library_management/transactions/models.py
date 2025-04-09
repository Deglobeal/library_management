from django.db import models
from django.utils import timezone
from Users.models import User
from books.models import Book
from django.conf import settings

class Transaction(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('RETURNED', 'Returned'),
        ('RETURN_REQUESTED', 'Return Requested'),
    ]
    modified = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions', limit_choices_to={'user_type': 'student'})
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='transactions')
    checkout_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(default=timezone.now() + timezone.timedelta(days=5))
    
    
    class Meta:
        ordering = ['-checkout_date']
        constraints = [
            models.UniqueConstraint(fields=['user', 'book'], condition=models.Q(return_date__isnull=True), name='active_book_transaction')
        ]
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.book.copies_available -= 1
            self.book.save()
            
        if self.return_date and not self._state.adding:  # If updating existing transaction
            original = Transaction.objects.get(pk=self.pk)
            if not original.return_date:
                self.book.copies_available += 1
                self.book.save()

        super().save(*args, **kwargs)

    def calculate_fine(self):
        """Calculate overdue fines if return is late"""
        if self.return_date and self.return_date > self.due_date:
            overdue_days = (self.return_date - self.due_date).days
            self.fine = overdue_days * 3  # Assuming a fine of $3 per day
            self.save(update_fields=['fine'])  # Save only the fine field

    def __str__(self):
        return f"{self.user.email} → {self.book.title} (Due: {self.due_date.date()})"
