# Generated by Django 2.2.16 on 2023-02-20 02:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0012_auto_20230220_0526'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['created']},
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['created']},
        ),
    ]
