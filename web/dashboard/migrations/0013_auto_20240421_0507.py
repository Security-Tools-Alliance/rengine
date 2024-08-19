# Generated by Django 3.2.4 on 2024-04-21 05:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0012_rename_is_ollama_ollamasettings_is_openai'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ollamasettings',
            name='is_openai',
        ),
        migrations.AddField(
            model_name='ollamasettings',
            name='is_ollama',
            field=models.BooleanField(default=True),
        ),
    ]
