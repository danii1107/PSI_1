# Generated by Django 4.2.10 on 2024-02-18 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0007_staff_alter_author_options'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Staff',
        ),
        migrations.AlterModelOptions(
            name='book',
            options={'ordering': ['title'], 'permissions': (('can_mark_returned', 'Set book as returned'),)},
        ),
        migrations.AlterModelOptions(
            name='bookinstance',
            options={'ordering': ['due_back']},
        ),
        migrations.AlterField(
            model_name='author',
            name='date_of_death',
            field=models.DateField(blank=True, null=True, verbose_name='died'),
        ),
    ]
