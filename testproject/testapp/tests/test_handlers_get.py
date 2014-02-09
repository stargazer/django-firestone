"""
This module tests the ``firestone.handlers.BaseHandler.get`` method
"""
from django.test import TestCase
from django.test import RequestFactory
from django.contrib.auth.models import User
from firestone.handlers import BaseHandler
from firestone.handlers import ModelHandler
from firestone import exceptions
from model_mommy import mommy

class TestBaseHandler(TestCase):
    def test_get_plural(self):
        handler = BaseHandler()            
        request = RequestFactory().get('/')

        self.assertRaises(
            exceptions.NotImplemented,
            handler.get,
            request,
        )

    def test_get_singular(self):
        handler = BaseHandler()            
        request = RequestFactory().get('/')

        self.assertRaises(
            exceptions.NotImplemented,
            handler.get,
            request, id=1,
        )

class TestModelHandler(TestCase):
    def setUp(self):
        mommy.make(User, 10)

    def test_get_plural(self):
        handler = ModelHandler()
        handler.model = User
        request = RequestFactory().get('/')

        self.assertItemsEqual(handler.get(request), User.objects.all())

    def test_get_singular_existing_item(self):
        handler = ModelHandler()
        handler.model = User
        request = RequestFactory().get('/')
        
        self.assertEqual(handler.get(request, id=1), User.objects.get(id=1))
        self.assertEqual(handler.get(request, id=10), User.objects.get(id=10))

    def test_get_singular_non_existing_item(self):
        handler = ModelHandler()
        handler.model = User
        request = RequestFactory().get('/')
        
        self.assertRaises(exceptions.Gone, handler.get, request, id=1000)
        self.assertRaises(exceptions.Gone, handler.get, request, id=100000)

    def test_get_singular_invalid_type(self):
        handler = ModelHandler()
        handler.model = User
        request = RequestFactory().get('/')

        self.assertRaises(exceptions.Gone, handler.get, request, id='string')
        self.assertRaises(exceptions.Gone, handler.get, request, id={'key': 'value'})
