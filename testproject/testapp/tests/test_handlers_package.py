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
        total = None
        res = handler.package(data, total, request)
        self.assertItemsEqual(res.keys(), ('data', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 1)

        data = 125.6
        total = None
        res = handler.package(data, total, request)
        self.assertItemsEqual(res.keys(), ('data', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 1)

        data = [1, 2, 3, 4, 5]
        total = 10
        res = handler.package(data, total, request)
        self.assertItemsEqual(res.keys(), ('data', 'total', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['total'], 10)
        self.assertEqual(res['count'], 5)

        data = {1, 2, 3, 4, 5}
        total = None
        res = handler.package(data, total, request)
        self.assertItemsEqual(res.keys(), ('data', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 5)
        
        data = {'key1': 'value1', 'key2': 'value2'}
        total = None
        res = handler.package(data, total, request)
        self.assertItemsEqual(res.keys(), ('data', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 2)

        data = mommy.make(User, 10)
        total = None
        res = handler.package(data, total, request)
        self.assertItemsEqual(res.keys(), ('data', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 10)

    def test_modelhandler_package(self):
        settings.DEBUG = False # No debug message will appear on response
        request = RequestFactory().get('whatever/')
        handler = ModelHandler()

        data = 'datastring'
        total = None
        res = handler.package(data, total, request)
        self.assertItemsEqual(res.keys(), ('data', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 1)

        data = 125.6
        total = None
        res = handler.package(data, total, request)
        self.assertItemsEqual(res.keys(), ('data', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 1)

        data = [1, 2, 3, 4, 5]
        total = None
        res = handler.package(data, total, request)
        self.assertItemsEqual(res.keys(), ('data', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 5)

        data = {1, 2, 3, 4, 5}
        total = 100
        res = handler.package(data, total, request)
        self.assertItemsEqual(res.keys(), ('data', 'total', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['total'], 100)
        self.assertEqual(res['count'], 5)
        
        data = {'key1': 'value1', 'key2': 'value2'}
        total = None
        res = handler.package(data, total, request)
        self.assertItemsEqual(res.keys(), ('data', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 2)

        data = mommy.make(User, 10)
        total = 100
        res = handler.package(data, total, request)
        self.assertItemsEqual(res.keys(), ('data', 'total', 'count'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['total'], 100)
        self.assertEqual(res['count'], 10)

    def test_modelhandler_package_debug(self):
        """
        I repeat the tests of the previous method, but with
        ``settings.debug=True``, which will return another key in the response.
        """
        settings.DEBUG = True
        request = RequestFactory().get('whatever/')
        handler = BaseHandler()

        data = 'datastring'
        total = None
        res = handler.package(data, total, request)
        self.assertItemsEqual(res.keys(), ('data', 'count', 'debug'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 1)

        data = 125.6
        total = None
        res = handler.package(data, total, request)
        self.assertItemsEqual(res.keys(), ('data', 'count', 'debug'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 1)

        data = [1, 2, 3, 4, 5]
        total = 100
        res = handler.package(data, total, request)
        self.assertItemsEqual(res.keys(), ('data', 'count', 'total', 'debug'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['total'], 100)
        self.assertEqual(res['count'], 5)

        data = {1, 2, 3, 4, 5}
        total = None
        res = handler.package(data, total, request)
        self.assertItemsEqual(res.keys(), ('data', 'count', 'debug'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 5)
        
        data = {'key1': 'value1', 'key2': 'value2'}
        total = None
        res = handler.package(data, total, request)
        self.assertItemsEqual(res.keys(), ('data', 'count', 'debug'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 2)

        data = mommy.make(User, 10)
        total = None
        res = handler.package(data, total, request)
        self.assertItemsEqual(res.keys(), ('data', 'count', 'debug'))
        self.assertEqual(res['data'], data)
        self.assertEqual(res['count'], 10)

            
