# transactions/admin.py
from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'checkout_date', 'due_date', 'return_date')
    list_filter = ('user__user_type', 'checkout_date', 'due_date')
    search_fields = ('user__email', 'book__title')
    date_hierarchy = 'checkout_date'
    ordering = ('-checkout_date',)