# transactions/admin.py
from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'checkout_date', 'due_date', 'return_date')
    list_filter = ('checkout_date', 'due_date')