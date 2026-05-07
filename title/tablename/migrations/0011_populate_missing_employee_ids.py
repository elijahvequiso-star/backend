from django.db import migrations


def unique_employee_id(Employee, preferred, used):
    candidate = preferred
    suffix = 2
    while candidate in used or Employee.objects.filter(employee_id=candidate).exists():
        candidate = f"{preferred}-{suffix}"
        suffix += 1
    used.add(candidate)
    return candidate


def populate_missing_employee_ids(apps, schema_editor):
    Employee = apps.get_model('tablename', 'Employee')
    used = set(Employee.objects.exclude(employee_id__isnull=True).exclude(employee_id='').values_list('employee_id', flat=True))

    for employee in Employee.objects.filter(employee_id__isnull=True).order_by('id'):
        normalized_name = (employee.name or '').strip().lower()
        if normalized_name == 'system administrator':
            preferred = 'ADMIN'
        elif normalized_name == 'hr manager':
            preferred = 'HR_MANAGER'
        else:
            preferred = f"EMP-{employee.id:06d}"
        employee.employee_id = unique_employee_id(Employee, preferred, used)
        employee.save(update_fields=['employee_id'])

    for employee in Employee.objects.filter(employee_id='').order_by('id'):
        preferred = f"EMP-{employee.id:06d}"
        employee.employee_id = unique_employee_id(Employee, preferred, used)
        employee.save(update_fields=['employee_id'])


class Migration(migrations.Migration):

    dependencies = [
        ('tablename', '0010_employee_preregistration'),
    ]

    operations = [
        migrations.RunPython(populate_missing_employee_ids, migrations.RunPython.noop),
    ]
