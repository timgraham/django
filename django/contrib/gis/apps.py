from django.apps import AppConfig
from django.core import serializers
from django.utils.translation import gettext_lazy as _


class GISConfig(AppConfig):
    default_auto_field = "django_mongodb.fields.MongoAutoField"
    name = "django.contrib.gis"
    verbose_name = _("GIS")

    def ready(self):
        serializers.BUILTIN_SERIALIZERS.setdefault(
            "geojson", "django.contrib.gis.serializers.geojson"
        )
