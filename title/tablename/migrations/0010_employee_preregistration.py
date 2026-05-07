# Generated manually for employee pre-registration and identity verification.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tablename', '0009_leave'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(choices=[('employee', 'Employee'), ('mason', 'Mason'), ('electrician', 'Electrician'), ('driver', 'Driver'), ('foreman', 'Foreman'), ('admin', 'Admin'), ('hr', 'HR')], max_length=20),
        ),
        migrations.AddField(
            model_name='employee',
            name='employee_id',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='first_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='employee',
            name='last_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='employee',
            name='middle_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='employee',
            name='mobile_number',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='employee',
            name='role',
            field=models.CharField(choices=[('employee', 'Employee'), ('mason', 'Mason'), ('electrician', 'Electrician'), ('driver', 'Driver'), ('foreman', 'Foreman'), ('admin', 'Admin'), ('hr', 'HR')], default='employee', max_length=20),
        ),
        migrations.AddField(
            model_name='employee',
            name='role_locked',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='employee',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_record', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='employee',
            name='identity_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='employee',
            name='identity_document_name',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.CreateModel(
            name='PasswordResetRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Rejected', 'Rejected')], default='Pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='password_reset_requests', to='tablename.employee')),
            ],
        ),
    ]
