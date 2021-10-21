# Generated by Django 3.2.7 on 2021-10-21 03:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('taiwan_einvoice', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='turnkeyweb',
            options={'permissions': (('view_te_einvoice', 'View E-Invoice'), ('print_te_einvoice', 'Print E-Invoice'))},
        ),
        migrations.CreateModel(
            name='UserConnectESCPOSWebLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('is_connected', models.BooleanField(default=True)),
                ('escpos_web', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='taiwan_einvoice.escposweb')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
