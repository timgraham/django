from __future__ import unicode_literals


import logging

from django.core.signals import got_request_exception
from django.dispatch import receiver
from django.test import TestCase
from django.test.utils import (setup_test_template_loader,
    restore_template_loaders, override_settings, patch_logger)
from django.utils.six import StringIO

from django.contrib.contenttypes.models import ContentType

from ..models import UrlArticle


@override_settings(ROOT_URLCONF='view_tests.urls')
class DefaultsTests(TestCase):
    """Test django views in django/views/defaults.py"""
    fixtures = ['testdata.json']
    non_existing_urls = ['/non_existing_url/',  # this is in urls.py
                         '/other_non_existing_url/']  # this NOT in urls.py

    def test_page_not_found(self):
        "A 404 status is returned by the page_not_found view"
        for url in self.non_existing_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)

    def test_csrf_token_in_404(self):
        """
        The 404 page should have the csrf_token available in the context
        """
        # See ticket #14565
        for url in self.non_existing_urls:
            response = self.client.get(url)
            csrf_token = response.context['csrf_token']
            self.assertNotEqual(str(csrf_token), 'NOTPROVIDED')
            self.assertNotEqual(str(csrf_token), '')

    def test_server_error(self):
        "The server_error view raises a 500 status"
        response = self.client.get('/server_error/')
        self.assertEqual(response.status_code, 500)


    def test_server_error_without_handler_error(self):
        """
        The server_error view raises a 500 status and while handling
        the error, the next error is raised.
        """

        @receiver(got_request_exception)
        def handler(sender, **kwargs):
            pass

        try:
            with patch_logger('django.request', 'error') as calls:
                try:
                    response = self.client.get('/views/raises_unhandled_exception/')
                except Exception as e:
                    # We need to catch the exceptions and check, if it is a 'Bad
                    # Request' or 'Bad Handler', since the Test Client will reraise
                    # these.
                    if str(e) not in ('Bad Request','Bad Handler'):
                        raise
                self.assertEqual(len(calls), 1)
                self.assertEqual(calls[0][0], 'Internal Server Error: /views/raises_unhandled_exception/')

        finally:
            got_request_exception.disconnect(handler)

    def test_server_error_with_handler_error(self):
        """
        The server_error view raises a 500 status and while handling
        the error, the next error is raised.
        """

        @receiver(got_request_exception)
        def handler(sender, **kwargs):
            raise Exception('Bad Handler')

        try:
            with patch_logger('django.request', 'error') as calls:
                try:
                    response = self.client.get('/views/raises_unhandled_exception/')
                except Exception as e:
                    # We need to catch the exceptions and check, if it is a 'Bad
                    # Request' or 'Bad Handler', since the Test Client will reraise
                    # these.
                    if str(e) not in ('Bad Request','Bad Handler'):
                        raise
                self.assertEqual(len(calls), 2)
                self.assertEqual(calls[0][0], 'Internal Server Error: /views/raises_unhandled_exception/')
                self.assertTrue(calls[1][0], 'Got Request Exception Handler Error: %s')
        finally:
            got_request_exception.disconnect(handler)

    def test_custom_templates(self):
        """
        Test that 404.html and 500.html templates are picked by their respective
        handler.
        """
        setup_test_template_loader(
            {'404.html': 'This is a test template for a 404 error.',
             '500.html': 'This is a test template for a 500 error.'}
        )
        try:
            for code, url in ((404, '/non_existing_url/'), (500, '/server_error/')):
                response = self.client.get(url)
                self.assertContains(response, "test template for a %d error" % code,
                    status_code=code)
        finally:
            restore_template_loaders()

    def test_get_absolute_url_attributes(self):
        "A model can set attributes on the get_absolute_url method"
        self.assertTrue(getattr(UrlArticle.get_absolute_url, 'purge', False),
                        'The attributes of the original get_absolute_url must be added.')
        article = UrlArticle.objects.get(pk=1)
        self.assertTrue(getattr(article.get_absolute_url, 'purge', False),
                        'The attributes of the original get_absolute_url must be added.')

    @override_settings(DEFAULT_CONTENT_TYPE="text/xml")
    def test_default_content_type_is_text_html(self):
        """
        Content-Type of the default error responses is text/html. Refs #20822.
        """
        response = self.client.get('/raises400/')
        self.assertEqual(response['Content-Type'], 'text/html')

        response = self.client.get('/raises403/')
        self.assertEqual(response['Content-Type'], 'text/html')

        response = self.client.get('/non_existing_url/')
        self.assertEqual(response['Content-Type'], 'text/html')

        response = self.client.get('/server_error/')
        self.assertEqual(response['Content-Type'], 'text/html')
