# Generated by Django 4.2.4 on 2023-11-14 01:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taiwan_einvoice', '0048_alter_batcheinvoice_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='legalentity',
            name='name',
            field=models.CharField(db_index=True, max_length=60),
        ),
    ]