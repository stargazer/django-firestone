"""
This module tests the ``firestone.handlers.HandlerControlFlow.cleanse_body``
method
"""
from django.test import TestCase
from django.test import RequestFactory
from firestone.handlers import BaseHandler
import json

def init_handler(handler, request, *args, **kwargs):
    # Mimicking the initialization of the handler instance
    handler.request = request
    handler.args = args
    handler.kwargs = kwargs
    return handler


class TestPOST(TestCase):
    def setUp(self):
        request = RequestFactory().post('/')
        handler = init_handler(BaseHandler(), request)
        handler.post_body_fields = (
            'id', 'name', 'surname',        
        )              

        self.handler = handler

    def test_dic(self):
        handler = self.handler
        handler.request.data = {
            'id': 1,
            'name': 'Name',
            'surname': 'Surname',
            'age': 'Age',
            'email': 'Email',
        }
        # Cleanse request body
        handler.cleanse_body()
        # And check
        self.assertItemsEqual(
            handler.request.data.keys(),
            handler.post_body_fields
        )

    def test_list(self):
        handler = self.handler
        handler.request.data = 10 * [{
            'id': 1,
            'name': 'Name',
            'surname': 'Surname',
            'age': 'Age',
            'email': 'Email',
        }]

        handler.cleanse_body()
        for item in handler.request.data:
            self.assertItemsEqual(
                item.keys(),
                handler.post_body_fields,
            )


class TestPUT(TestCase):
    def test_dic(self):
        request = RequestFactory().put('/')

        handler = init_handler(BaseHandler(), request)
        handler.put_body_fields = ['id', 'name']
        handler.request.data = {
            'id': 1,
            'name': 'Name',
            'surname': 'Surname',
            'age': 'Age',
            'email': 'Email',
        }

        # Cleanse request body
        handler.cleanse_body()
        # And check
        self.assertItemsEqual(
            handler.request.data.keys(),
            handler.put_body_fields
        )
