# Generated by Django 5.1.7 on 2025-04-05 07:26

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0004_book_added_by_book_date_added_book_last_updated'),
        ('transactions', '0004_alter_transaction_due_date'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='currently_borrowed',
            field=models.ManyToManyField(blank=True, related_name='borrowed_books', through='transactions.Transaction', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='book',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], default='PENDING', max_length=10),
        ),
    ]
