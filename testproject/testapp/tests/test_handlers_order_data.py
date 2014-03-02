"""
This module tests the ``firestone.handler.BaseHandler.order_data`` method
"""
from firestone.handlers import BaseHandler
from firestone.handlers import ModelHandler
from django.test import TestCase
from django.test import RequestFactory
from django.contrib.auth.models import User
from model_mommy import mommy


class TestBaseHandlerOrderData(TestCase):
    def test_order_data(self):
        handler = BaseHandler()
        request = RequestFactory().get('/')
        data = 'data'
        order = 'someorder'

        self.assertEqual(
            handler.order_data(data, order, request),
            data
        )

class TestModelHandlerOrderData(TestCase):
    def setUp(self):
        mommy.make(User, 100)

    def test_order_data_plural(self):
        handler = ModelHandler()
        handler.model = User
        request = RequestFactory().get('/')
        data = User.objects.all()
        order = 'someorder'

        self.assertEqual(
            handler.order_data(data, order, request),
            data,
        )

    def test_order_data_singular(self):
        handler = ModelHandler()
        handler.model = User
        request = RequestFactory().get('/')
        data = User.objects.get(id=1)
        order = 'someorder'

        # TODO: I should probably throw an error here.
        self.assertEqual(
            handler.order_data(data, order, request),
            data,
        )


