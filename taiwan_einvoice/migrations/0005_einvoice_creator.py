# Generated by Django 3.2.7 on 2021-10-13 04:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('taiwan_einvoice', '0004_einvoice_generate_batch_no_sha1'),
    ]

    operations = [
        migrations.AddField(
            model_name='einvoice',
            name='creator',
            field=models.ForeignKey(default=102, on_delete=django.db.models.deletion.DO_NOTHING, to='auth.user'),
            preserve_default=False,
        ),
    ]
