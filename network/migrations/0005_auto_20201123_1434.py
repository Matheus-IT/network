# Generated by Django 3.1.2 on 2020-11-23 17:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0004_auto_20201106_1452'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='likes',
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('liker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to=settings.AUTH_USER_MODEL)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='network.post')),
            ],
        ),
    ]
