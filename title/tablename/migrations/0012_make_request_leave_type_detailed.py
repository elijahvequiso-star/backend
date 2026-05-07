from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tablename', '0011_populate_missing_employee_ids'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='type',
            field=models.TextField(default='General'),
        ),
        migrations.AlterField(
            model_name='leave',
            name='type',
            field=models.TextField(default='Leave request'),
        ),
    ]
