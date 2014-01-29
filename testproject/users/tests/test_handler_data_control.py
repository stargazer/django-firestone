"""
This module tests the ``get_data``, ``get_data_item``, ``get_data_set`` and
``get_working_set`` handler methods.
"""

from firestone.handlers import BaseHandler
from firestone.handlers import ModelHandler
from django.test import TestCase
from django.test import RequestFactory
from django.contrib.auth.models import User
from model_mommy import mommy

def setup_handler(handler, request, *args, **kwargs):
    """
    Mimics the behavior of ``firestone.proxy.Proxy.__call__``, without of course
    invoking the handler.
    """
    handler.request = request
    handler.args = args
    handler.kwargs = kwargs
    return handler

class TestBaseHandlerDataControl(TestCase):
    def setUp(self):
        self.request = RequestFactory().get('whateverpath/')
        self.handler = setup_handler(BaseHandler(), self.request)

    def test_get_data_item(self):
        # Testing ``BaseHandler.get_item``
        request = self.request
        handler = self.handler

        self.assertEquals(
            handler.get_data_item(request),
            None,
        )

    def test_get_data_set(self):        
        # Testing ``BaseHandler.get_data_set``
        request = self.request
        handler = self.handler

        self.assertEquals(
            handler.get_data_set(request),
            None,
        )

    def test_get_working_set(self):        
        # Testing ``BaseHandler.get_working_set``
        request = self.request
        handler = self.handler

        self.assertEquals(
            handler.get_working_set(request),
            None,
        )

    def test_get_data(self):        
        # Testing ``BaseHandler.get_data``
        request = self.request
        handler = self.handler
        
        self.assertEquals(
            handler.get_data(request),
            None,
        )

class testModelHandlerDataControl(TestCase):
    def setUp(self):
        self.request = RequestFactory().get('whateverpath/')
        self.handler = setup_handler(ModelHandler(), self.request)
        self.handler.model = User

        # Create some model instances
        users = mommy.make(User, 10)

    def test_get_data_item(self):
        # Testing ``ModelHandler.get_data_item``
        request = self.request
        handler = self.handler
        
        self.assertEquals(
            handler.get_data_item(request),
            None,
        )
        self.assertEquals(
            handler.get_data_item(request, id=1),
            User.objects.get(id=1),
        )
        self.assertEquals(
            handler.get_data_item(request, id=10),
            User.objects.get(id=10),
        )
        self.assertRaises(
            User.DoesNotExist,
            handler.get_data_item, request, id=1000,
        )

    def test_get_data_set(self):        
        # Testing ``ModelHandler.get_data_set``
        request = self.request
        handler = self.handler
        
        self.assertItemsEqual(
            handler.get_data_set(request),
            User.objects.all(),
        )

    def test_get_working_set(self):        
        # Testing ``ModelHandler.get_working_set``
        request = self.request
        handler = self.handler
        
        self.assertItemsEqual(
            handler.get_working_set(request),
            User.objects.all(),
        )

    def test_get_data(self):        
        # Testing ``ModelHandler.get_data``
        request = self.request
        handler = self.handler
        
        self.assertItemsEqual(
            handler.get_data(request),
            User.objects.all(),
        )
        self.assertEquals(
            handler.get_data(request, id=1),
            User.objects.get(id=1),
        )
        self.assertEquals(
            handler.get_data(request, id=10),
            User.objects.get(id=10),
        )
        self.assertRaises(
            User.DoesNotExist,
            handler.get_data, request, id=1000,
        )


