from django_mongodb_backend.fields import ObjectIdAutoField

from django.db import migrations, models


class Migration(migrations.Migration):
    operations = [
        migrations.CreateModel(
            "Author",
            [
                ("id", ObjectIdAutoField(primary_key=True)),
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(null=True)),
                ("age", models.IntegerField(default=0)),
                ("silly_field", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            "Tribble",
            [
                ("id", ObjectIdAutoField(primary_key=True)),
                ("fluffy", models.BooleanField(default=True)),
            ],
        ),
    ]
