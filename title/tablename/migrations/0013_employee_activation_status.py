from django.db import migrations, models


def normalize_employee_activation(apps, schema_editor):
    Employee = apps.get_model('tablename', 'Employee')
    for employee in Employee.objects.all():
        employee.is_registered = bool(employee.user_id)
        if employee.user_id or employee.status == 'Active':
            employee.status = 'ACTIVE'
        else:
            employee.status = 'PENDING'
        employee.save(update_fields=['is_registered', 'status'])


class Migration(migrations.Migration):

    dependencies = [
        ('tablename', '0012_make_request_leave_type_detailed'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='is_registered',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='employee',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('ACTIVE', 'Active')], default='PENDING', max_length=10),
        ),
        migrations.RunPython(normalize_employee_activation, migrations.RunPython.noop),
    ]
