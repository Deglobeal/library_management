# Generated by Django 5.1.7 on 2025-04-09 18:49

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0007_alter_transaction_due_date_alter_transaction_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='due_date',
            field=models.DateTimeField(default=datetime.datetime(2025, 4, 14, 18, 49, 58, 684092, tzinfo=datetime.timezone.utc)),
        ),
    ]
