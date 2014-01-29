"""
This module tests the ``firestone.handlers.HandlerDataFlow.add_metadata``
method.
"""
from firestone.handlers import BaseHandler
from firestone.handlers import ModelHandler
from django.test import TestCase
from django.test import RequestFactory
from django.contrib.auth.models import User
from model_mommy import mommy


class TestPackage(TestCase):
    """
    I simply check whether the result of ``add_metadata`` is a dictionary
    """
    def test_basehandler_add_metadata(self):
        request = RequestFactory().get('/')
        handler = BaseHandler()

        data = {'data': 'somestring'}
        self.assertTrue(isinstance(handler.add_metadata(data, request), dict))

        data = {'data': [1, 2, 3, 4]}
        self.assertTrue(isinstance(handler.add_metadata(data, request), dict))

        data = {'data': {'key': 'value'}}
        self.assertTrue(isinstance(handler.add_metadata(data, request), dict))

        data = {'dict': mommy.make(User, 10)}
        self.assertTrue(isinstance(handler.add_metadata(data, request), dict))

    def test_modelhandler_add_metadata(self):
        request = RequestFactory().get('/')
        handler = ModelHandler()

        data = {'data': 'somestring'}
        self.assertTrue(isinstance(handler.add_metadata(data, request), dict))

        data = {'data': [1, 2, 3, 4]}
        self.assertTrue(isinstance(handler.add_metadata(data, request), dict))

        data = {'data': {'key': 'value'}}
        self.assertTrue(isinstance(handler.add_metadata(data, request), dict))

        data = {'dict': mommy.make(User, 10)}
        self.assertTrue(isinstance(handler.add_metadata(data, request), dict))


