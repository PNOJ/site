# Generated by Django 3.0.8 on 2020-07-05 02:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0023_auto_20200704_2318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='language',
            field=models.CharField(choices=[('python3', 'Python 3'), ('java8', 'Java 8'), ('cpp17', 'C++17'), ('haskell', 'Haskell'), ('brainfuck', 'Brainfuck'), ('c18', 'C18'), ('java11', 'Java 11'), ('scratch', 'Scratch'), ('text', 'Text')], max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='main_language',
            field=models.CharField(choices=[('python3', 'Python 3'), ('java8', 'Java 8'), ('cpp17', 'C++17'), ('haskell', 'Haskell'), ('brainfuck', 'Brainfuck'), ('c18', 'C18'), ('java11', 'Java 11'), ('scratch', 'Scratch'), ('text', 'Text')], default='python3', max_length=10),
        ),
    ]
