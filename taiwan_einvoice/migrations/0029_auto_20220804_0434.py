# Generated by Django 3.2.10 on 2022-08-04 04:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taiwan_einvoice', '0028_alter_audittype_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='summaryreport',
            name='failed_counts',
            field=models.JSONField(default={}),
        ),
        migrations.AlterField(
            model_name='summaryreport',
            name='good_counts',
            field=models.JSONField(default={}),
        ),
        migrations.AlterField(
            model_name='summaryreport',
            name='problems',
            field=models.JSONField(default={}),
        ),
        migrations.AlterField(
            model_name='summaryreport',
            name='resolved_counts',
            field=models.JSONField(default={}),
        ),
    ]