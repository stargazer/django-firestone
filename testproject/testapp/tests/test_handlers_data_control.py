"""
This module tests the ``get_data``, ``get_data_item``, ``get_data_set`` and
``get_working_set`` handler methods.
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

class testModelHandlerDataControl(TestCase):
    def setUp(self):
        request = RequestFactory().get('whateverpath/')

        handler = init_handler(ModelHandler(), request)
        handler.model = User
        self.handler = handler

        # Create some model instances
        users = mommy.make(User, 10)

    def test_get_data_item(self):
        # Testing ``ModelHandler.get_data_item``
        handler = self.handler
        
        self.assertEquals(
            handler.get_data_item(),
            None,
        )

        handler.kwargs = {'id':1}
        self.assertEquals(
            handler.get_data_item(),
            User.objects.get(id=1),
        )

        # Instance selection based on 2 fields
        user = User.objects.get(id=1)
        handler.kwargs = {'id': user.id, 'first_name': user.first_name}
        self.assertEquals(
            handler.get_data_item(),
            user,
        )

        handler.kwargs = {'id': 10}
        self.assertEquals(
            handler.get_data_item(),
            User.objects.get(id=10),
        )

        # ObjectDoesNotExist becomes exceptions.Gone
        handler.kwargs = {'id': 1000}
        self.assertRaises(
            exceptions.Gone,
            handler.get_data_item,
        )

        # ValueError becomes exceptions.Gone
        handler.kwargs = {'id': 'string'}
        self.assertRaises(
            exceptions.Gone,
            handler.get_data_item,
        )

        # TypeError becomes exceptions.Gone
        handler.kwargs = {'id': {'key': 'value'}}
        self.assertRaises(
            exceptions.Gone,
            handler.get_data_item,
        )

    def test_get_data_set(self):        
        # Testing ``ModelHandler.get_data_set``
        handler = self.handler
        
        self.assertItemsEqual(
            handler.get_data_set(),
            User.objects.all(),
        )

    def test_get_working_set(self):        
        # Testing ``ModelHandler.get_working_set``
        handler = self.handler
        
        self.assertItemsEqual(
            handler.get_working_set(),
            User.objects.all(),
        )

    def test_get_data(self):        
        # Testing ``ModelHandler.get_data``
        handler = self.handler
        
        self.assertItemsEqual(
            handler.get_data(),
            User.objects.all(),
        )

        handler.kwargs = {'id': 1}
        self.assertEquals(
            handler.get_data(),
            User.objects.get(id=1),
        )

        handler.kwargs = {'id': 10}
        self.assertEquals(
            handler.get_data(),
            User.objects.get(id=10),
        )

        handler.kwargs = {'id': 1000}
        self.assertRaises(
            exceptions.Gone,
            handler.get_data,
        )


