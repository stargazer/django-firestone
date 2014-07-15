"""
This module tests the ``firestone.handlers.BaseHandler.is_catastrophic``
methods
"""
from firestone.handlers import BaseHandler
from firestone.handlers import ModelHandler
from firestone import exceptions
from django.test import TestCase
from django.test import RequestFactory
from django.contrib.auth.models import User
from model_mommy import mommy

def init_handler(handler, request, *args, **kwargs):
    # Mimicking the initialization of the handler instance
    handler.request = request
    handler.args = args
    handler.kwargs = kwargs
    return handler

class TestBaseHandlerIsCatastrophic(TestCase):
    def test_plural_delete_not_allowed(self):
        """
        Plural DELETE is not allowed, so ``is_catastrophic`` will return True
        """
        request = RequestFactory().delete('/')
        handler = init_handler(BaseHandler(), request)
        
        self.assertTrue(handler.is_catastrophic())

    def test_plural_delete_allowed(self):
        """
        Plural DELETE is allowed, so ``is_catastrophic`` will return False
        """
        request = RequestFactory().delete('/')
        handler = init_handler(BaseHandler(), request)
        handler.http_methods = ('PLURAL_DELETE',)

        self.assertFalse(handler.is_catastrophic())


    def test_plural_put_not_allowed(self):
        request = RequestFactory().put('/')
        handler = init_handler(BaseHandler(), request)

        self.assertTrue(handler.is_catastrophic())

    def test_plural_put_allowed(self):
        request = RequestFactory().put('/')
        handler = init_handler(BaseHandler(), request)
        handler.http_methods = ('PLURAL_PUT',)

        self.assertFalse(handler.is_catastrophic())
