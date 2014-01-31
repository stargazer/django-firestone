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

class TestPackage(TestCase):
    def test_basehandler_package(self):
        settings.DEBUG = False # No debug message will appear on response
        request = RequestFactory().get('whatever/')
        handler = BaseHandler()

        data = 'datastring'
        res = handler.package(data, request)
        self.assertItemsEqual(res.keys(), ('data', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 1)

        data = 125.6
        res = handler.package(data, request)
        self.assertItemsEqual(res.keys(), ('data', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 1)

        data = [1, 2, 3, 4, 5]
        res = handler.package(data, request)
        self.assertItemsEqual(res.keys(), ('data', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 5)

        data = {1, 2, 3, 4, 5}
        res = handler.package(data, request)
        self.assertItemsEqual(res.keys(), ('data', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 5)
        
        data = {'key1': 'value1', 'key2': 'value2'}
        res = handler.package(data, request)
        self.assertItemsEqual(res.keys(), ('data', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 2)

        data = mommy.make(User, 10)
        res = handler.package(data, request)
        self.assertItemsEqual(res.keys(), ('data', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 10)

    def test_modelhandler_package(self):
        settings.DEBUG = False # No debug message will appear on response
        request = RequestFactory().get('whatever/')
        handler = ModelHandler()

        data = 'datastring'
        res = handler.package(data, request)
        self.assertItemsEqual(res.keys(), ('data', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 1)

        data = 125.6
        res = handler.package(data, request)
        self.assertItemsEqual(res.keys(), ('data', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 1)

        data = [1, 2, 3, 4, 5]
        res = handler.package(data, request)
        self.assertItemsEqual(res.keys(), ('data', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 5)

        data = {1, 2, 3, 4, 5}
        res = handler.package(data, request)
        self.assertItemsEqual(res.keys(), ('data', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 5)
        
        data = {'key1': 'value1', 'key2': 'value2'}
        res = handler.package(data, request)
        self.assertItemsEqual(res.keys(), ('data', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 2)

        data = mommy.make(User, 10)
        res = handler.package(data, request)
        self.assertItemsEqual(res.keys(), ('data', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 10)

    def test_modelhandler_package(self):
        """
        I repeat the tests of the previous method, but with
        ``settings.debug=True``, which will return another key in the response.
        """
        settings.DEBUG = True
        request = RequestFactory().get('whatever/')
        handler = BaseHandler()

        data = 'datastring'
        res = handler.package(data, request)
        self.assertItemsEqual(res.keys(), ('data', 'count', 'debug'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 1)

        data = 125.6
        res = handler.package(data, request)
        self.assertItemsEqual(res.keys(), ('data', 'count', 'debug'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 1)

        data = [1, 2, 3, 4, 5]
        res = handler.package(data, request)
        self.assertItemsEqual(res.keys(), ('data', 'count', 'debug'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 5)

        data = {1, 2, 3, 4, 5}
        res = handler.package(data, request)
        self.assertItemsEqual(res.keys(), ('data', 'count', 'debug'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 5)
        
        data = {'key1': 'value1', 'key2': 'value2'}
        res = handler.package(data, request)
        self.assertItemsEqual(res.keys(), ('data', 'count', 'debug'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 2)

        data = mommy.make(User, 10)
        res = handler.package(data, request)
        self.assertItemsEqual(res.keys(), ('data', 'count', 'debug'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 10)

            
