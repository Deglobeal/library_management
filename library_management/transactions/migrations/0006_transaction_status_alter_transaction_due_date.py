# Generated by Django 5.1.7 on 2025-04-09 17:42

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0005_alter_transaction_options_alter_transaction_due_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected'), ('RETURNED', 'Returned')], default='PENDING', max_length=10),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='due_date',
            field=models.DateTimeField(default=datetime.datetime(2025, 4, 14, 17, 42, 19, 864175, tzinfo=datetime.timezone.utc)),
        ),
    ]
