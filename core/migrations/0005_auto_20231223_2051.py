# Generated by Django 3.2.23 on 2023-12-23 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20231222_2355'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='keywords',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='post',
            name='tags',
            field=models.ManyToManyField(related_name='tags', to='core.Tag'),
        ),
    ]
