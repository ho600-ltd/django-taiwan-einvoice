# Generated by Django 3.2.14 on 2022-07-21 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('turnkey_wrapper', '0008_auto_20220721_0659'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eiturnkeybatch',
            name='turnkey_version',
            field=models.CharField(choices=[('3.2', '3.2')], default='3.2', max_length=8),
        ),
    ]