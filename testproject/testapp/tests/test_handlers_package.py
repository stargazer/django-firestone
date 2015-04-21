"""
This module tests the ``firestone.handlers.HandlerDataFlow.package`` method
"""
from firestone.handlers import BaseHandler
from firestone.handlers import ModelHandler
from django.test import TestCase
from django.test import RequestFactory
from django.contrib.auth.models import User
from django.conf import settings
from model_mommy import mommy

def init_handler(handler, request, *args, **kwargs):
    # Mimicking the initialization of the handler instance
    handler.request = request
    handler.args = args
    handler.kwargs = kwargs
    return handler


class TestPackage(TestCase):
    def test_basehandler_package(self):
        settings.DEBUG = False # No debug message will appear on response
        request = RequestFactory().get('whatever/')
        handler = init_handler(BaseHandler(), request)

        data = 'datastring'
        pagination = {}
        res = handler.package(data, pagination)
        self.assertItemsEqual(res.keys(), ('data', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 1)

        data = 125.6
        pagination = {}
        res = handler.package(data, pagination)
        self.assertItemsEqual(res.keys(), ('data', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 1)

        data = [1, 2, 3, 4, 5]
        pagination = {'key': 'value'}
        res = handler.package(data, pagination)
        self.assertItemsEqual(res.keys(), ('data', 'pagination', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['pagination'], pagination)
        self.assertEqual(res['count'], 5)

        data = {1, 2, 3, 4, 5}
        pagination = {}
        res = handler.package(data, pagination)
        self.assertItemsEqual(res.keys(), ('data', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 5)
        
        data = {'key1': 'value1', 'key2': 'value2'}
        pagination = {}
        res = handler.package(data, pagination)
        self.assertItemsEqual(res.keys(), ('data', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 2)

        data = mommy.make(User, 10)
        pagination = {}
        res = handler.package(data, pagination)
        self.assertItemsEqual(res.keys(), ('data', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 10)

    def test_modelhandler_package(self):
        settings.DEBUG = False # No debug message will appear on response
        request = RequestFactory().get('whatever/')
        handler = ModelHandler()

        data = 'datastring'
        pagination = {}
        res = handler.package(data, pagination)
        self.assertItemsEqual(res.keys(), ('data', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 1)

        data = 125.6
        pagination = {}
        res = handler.package(data, pagination)
        self.assertItemsEqual(res.keys(), ('data', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 1)

        data = [1, 2, 3, 4, 5]
        pagination = None
        res = handler.package(data, pagination)
        self.assertItemsEqual(res.keys(), ('data', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 5)

        data = {1, 2, 3, 4, 5}
        pagination = {'key': 'value'}
        res = handler.package(data, pagination)
        self.assertItemsEqual(res.keys(), ('data', 'pagination', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['pagination'], pagination)
        self.assertEqual(res['count'], 5)
        
        data = {'key1': 'value1', 'key2': 'value2'}
        pagination = {}
        res = handler.package(data, pagination)
        self.assertItemsEqual(res.keys(), ('data', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 2)

        data = mommy.make(User, 10)
        pagination = {'key': 'value'}
        res = handler.package(data, pagination)
        self.assertItemsEqual(res.keys(), ('data', 'pagination', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['pagination'], pagination)
        self.assertEqual(res['count'], 10)

    def test_modelhandler_package_debug(self):
        """
        I repeat the tests of the previous method, but with
        ``settings.debug=True``, which will return another key in the response.
        """
        settings.DEBUG = True
        request = RequestFactory().get('whatever/')
        handler = init_handler(BaseHandler(), request)

        data = 'datastring'
        pagination = {}
        import pdb; pdb.set_trace()
        res = handler.package(data, pagination)
        self.assertItemsEqual(res.keys(), ('data', 'count', 'debug'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 1)

        data = 125.6
        pagination = {}
        res = handler.package(data, pagination)
        self.assertItemsEqual(res.keys(), ('data', 'count', 'debug'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 1)

        data = [1, 2, 3, 4, 5]
        pagination = {'key': 'value'}
        res = handler.package(data, pagination)
        self.assertItemsEqual(res.keys(), ('data', 'count', 'pagination', 'debug'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['pagination'], pagination)
        self.assertEqual(res['count'], 5)

        data = {1, 2, 3, 4, 5}
        pagination = {}
        res = handler.package(data, pagination)
        self.assertItemsEqual(res.keys(), ('data', 'count', 'debug'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 5)
        
        data = {'key1': 'value1', 'key2': 'value2'}
        pagination = {}
        res = handler.package(data, pagination)
        self.assertItemsEqual(res.keys(), ('data', 'count', 'debug'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 2)

        data = mommy.make(User, 10)
        pagination = {}
        res = handler.package(data, pagination)
        self.assertItemsEqual(res.keys(), ('data', 'count', 'debug'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 10)

            
