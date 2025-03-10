# Generated by Django 5.1.7 on 2025-03-10 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100)),
                ('email', models.CharField(max_length=100, unique=True)),
                ('user_id', models.CharField(max_length=10, unique=True)),
                ('department', models.CharField(max_length=100)),
                ('identification', models.CharField(choices=[('student', 'Student'), ('staff', 'Staff'), ('admin', 'Admin')], default='student', max_length=10)),
            ],
        ),
    ]
