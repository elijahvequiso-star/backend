import django.db.models.deletion
from django.db import migrations, models


def populate_payroll_sites(apps, schema_editor):
    Payroll = apps.get_model('tablename', 'Payroll')
    for payroll in Payroll.objects.filter(site__isnull=True).select_related('employee__site'):
        if payroll.employee and payroll.employee.site_id:
            payroll.site_id = payroll.employee.site_id
            payroll.save(update_fields=['site'])


class Migration(migrations.Migration):

    dependencies = [
        ('tablename', '0014_payroll_week_end'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='site',
            options={'ordering': ['name', 'location']},
        ),
        migrations.AddField(
            model_name='payroll',
            name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payrolls', to='tablename.site'),
        ),
        migrations.RunPython(populate_payroll_sites, migrations.RunPython.noop),
        migrations.AlterUniqueTogether(
            name='payroll',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='site',
            constraint=models.UniqueConstraint(fields=('name', 'location'), name='unique_site_name_location'),
        ),
        migrations.AddConstraint(
            model_name='payroll',
            constraint=models.UniqueConstraint(fields=('employee', 'site', 'week_start'), name='unique_employee_site_week_payroll'),
        ),
        migrations.AddIndex(
            model_name='payroll',
            index=models.Index(fields=['site', 'week_start'], name='tablename_p_site_i_913165_idx'),
        ),
        migrations.AddIndex(
            model_name='payroll',
            index=models.Index(fields=['week_start', 'site'], name='tablename_p_week_st_ff5995_idx'),
        ),
    ]
