# Generated by Django 3.2.10 on 2022-08-04 04:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taiwan_einvoice', '0029_auto_20220804_0434'),
    ]

    operations = [
        migrations.AddField(
            model_name='canceleinvoice',
            name='ei_audited',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='einvoice',
            name='ei_audited',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='voideinvoice',
            name='ei_audited',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
