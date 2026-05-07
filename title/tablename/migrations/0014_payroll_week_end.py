from datetime import timedelta

from django.db import migrations, models


def populate_week_end(apps, schema_editor):
    Payroll = apps.get_model('tablename', 'Payroll')
    for payroll in Payroll.objects.filter(week_end__isnull=True):
        payroll.week_end = payroll.week_start + timedelta(days=6)
        payroll.save(update_fields=['week_end'])


class Migration(migrations.Migration):

    dependencies = [
        ('tablename', '0013_employee_activation_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='payroll',
            name='week_end',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.RunPython(populate_week_end, migrations.RunPython.noop),
    ]
