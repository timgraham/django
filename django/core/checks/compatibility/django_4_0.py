from django.conf import settings

from .. import Error, Tags, register


@register(Tags.compatibility)
def check_csrf_trusted_origins(app_configs, **kwargs):
    for origin in settings.CSRF_TRUSTED_ORIGINS:
        if not (origin.startswith('http://') or origin.startswith('https://')):
            return [Error(
                'As of Django 4.0, the values in the CSRF_TRUSTED_ORIGINS '
                'setting must start with http:// or https:// (found %s). '
                'Read the release notes for details.' % origin,
                id='4_0.E001',
            )]
    return []
