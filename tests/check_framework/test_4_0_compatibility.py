from django.core.checks.compatibility.django_4_0 import (
    check_csrf_trusted_origins,
)
from django.test import SimpleTestCase
from django.test.utils import override_settings


class CheckCSRFTrustedOrigins(SimpleTestCase):

    @override_settings(CSRF_TRUSTED_ORIGINS=['example.com'])
    def test_invalid_url(self):
        result = check_csrf_trusted_origins(None)
        self.assertEqual(result[0].id, '4_0.E001')
        self.assertEqual(
            result[0].msg,
            'As of Django 4.0, the values in the CSRF_TRUSTED_ORIGINS setting '
            'must start with http:// or https:// (found example.com). Read '
            'the release notes for details.'
        )

    @override_settings(
        CSRF_TRUSTED_ORIGINS=['http://example.com', 'https://example.com'],
    )
    def test_valid_urls(self):
        result = check_csrf_trusted_origins(None)
        self.assertEqual(len(result), 0)
