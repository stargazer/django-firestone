"""
This module tests the ``firestone.handlers.HandlerDataFlow.package`` method
"""
from firestone.handlers import BaseHandler
from firestone.handlers import ModelHandler
from django.test import TestCase
from django.test import RequestFactory
from django.contrib.auth.models import User
from model_mommy import mommy

def setup_handler(handler, request, *args, **kwargs):
    handler.request = request
    handler.args = args
    handler.kwargs = kwargs
    return handler

class TestPackage(TestCase):
    def test_basehandler_package(self):
        request = RequestFactory().get('whatever/')
        handler = setup_handler(BaseHandler(), request)

        data = 'datastring'
        self.assertEqual(
            handler.package(data, request), 
            {'data': data, 'count': 1}
        )

        data = 125.6
        self.assertEqual(
            handler.package(data, request), 
            {'data': data, 'count': 1}
        )

        data = [1, 2, 3, 4, 5]
        self.assertEqual(
            handler.package(data, request), 
            {'data': data, 'count': 5}
        )

        data = {1, 2, 3, 4, 5}
        self.assertEqual(
            handler.package(data, request), 
            {'data': data, 'count': 5}
        )
        
        data = {'key1': 'value1', 'key2': 'value2'}
        self.assertEqual(
            handler.package(data, request), 
            {'data': data, 'count': 2}
        )

        data = mommy.make(User, 10)
        self.assertEqual(
            handler.package(data, request), 
            {'data': data, 'count': 10}
        )

    def test_modelhandler_package(self):
        request = RequestFactory().get('whatever/')
        handler = setup_handler(BaseHandler(), request)

        data = 'datastring'
        self.assertEqual(
            handler.package(data, request), 
            {'data': data, 'count': 1}
        )

        data = 125.6
        self.assertEqual(
            handler.package(data, request), 
            {'data': data, 'count': 1}
        )

        data = [1, 2, 3, 4, 5]
        self.assertEqual(
            handler.package(data, request), 
            {'data': data, 'count': 5}
        )

        data = {1, 2, 3, 4, 5}
        self.assertEqual(
            handler.package(data, request), 
            {'data': data, 'count': 5}
        )
        
        data = {'key1': 'value1', 'key2': 'value2'}
        self.assertEqual(
            handler.package(data, request), 
            {'data': data, 'count': 2}
        )

        data = mommy.make(User, 10)
        self.assertEqual(
            handler.package(data, request), 
            {'data': data, 'count': 10}
        )
