# Generated by Django 5.0.1 on 2024-05-18 22:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("file_versions", "0004_document_created_at_document_file_location_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="document",
            name="file_location",
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name="file",
            name="digest",
            field=models.CharField(max_length=32, unique=True),
        ),
    ]
