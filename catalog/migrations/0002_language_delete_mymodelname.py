# Generated by Django 4.2.9 on 2024-02-07 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Ingrese el nombre del lenguaje (por ejemplo, Inglés, Español, Francés, etc.)', max_length=200)),
            ],
        ),
        migrations.DeleteModel(
            name='MyModelName',
        ),
    ]
