"""
This module tests the ``firestone.handlers.HandlerControlFlow.cleanse_body``
method
"""
from django.test import TestCase
from django.test import RequestFactory
from firestone.handlers import BaseHandler
import json

class TestPOST(TestCase):
    def setUp(self):
        self.handler = BaseHandler()
        self.handler.post_body_fields = (
            'id', 'name', 'surname',        
        )              

    def test_dic(self):
        handler = self.handler
        request = RequestFactory().post('/')
        request.data = {
            'id': 1,
            'name': 'Name',
            'surname': 'Surname',
            'age': 'Age',
            'email': 'Email',
        }
        # Cleanse request body
        handler.cleanse_body(request)
        # And check
        self.assertItemsEqual(
            request.data.keys(),
            handler.post_body_fields
        )

    def test_list(self):
        handler = self.handler
        request = RequestFactory().post('/')
        request.data = 10 * [{
            'id': 1,
            'name': 'Name',
            'surname': 'Surname',
            'age': 'Age',
            'email': 'Email',
        }]

        handler.cleanse_body(request)
        for item in request.data:
            self.assertItemsEqual(
                item.keys(),
                handler.post_body_fields,
            )


class TestPUT(TestCase):
    def test_dic(self):
        handler = BaseHandler()
        handler.put_body_fields = ['id', 'name']
        request = RequestFactory().put('/')
        request.data = {
            'id': 1,
            'name': 'Name',
            'surname': 'Surname',
            'age': 'Age',
            'email': 'Email',
        }
        # Cleanse request body
        handler.cleanse_body(request)
        # And check
        self.assertItemsEqual(
            request.data.keys(),
            handler.put_body_fields
        )
