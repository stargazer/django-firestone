"""
This module tests the ``firestone.handlers.BaseHandler.order`` method
"""
from firestone.handlers import BaseHandler
from firestone.handlers import ModelHandler
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


class TestBaseHandlerOrder(TestCase):
    def setUp(self):
        request = RequestFactory().get('/')
        handler = init_handler(BaseHandler(), request)
        self.handler = handler

    def test_no_ordering(self):
        handler = self.handler

        data = 'whatever'
        self.assertEqual(
            handler.order(data),
            data
        )

    def test_ordering(self):
        handler = self.handler
        data = 'whatever'

        self.assertEqual(
            handler.order(data),
            data
        )

class TestModelHandlerOrder(TestCase):
    def setUp(self):
        request = RequestFactory().get('/')
        handler = init_handler(ModelHandler(), request)
        handler.model = User
        self.handler = handler

        mommy.make(User, 100)

    def test_order_default(self):
        data = User.objects.all()
        self.assertEqual(
            self.handler.order(data),
            data,
        )

    def test_order_descending(self):
        def order(data):
            " Descending order"
            return data.order_by('-id')
        handler = self.handler
        handler.order = order

        data = User.objects.all()
        ordered_data = handler.order(data)

        # Check if indeed the order of ``ordered_data`` is descending.
        self.assertEqual(ordered_data[0], User.objects.get(id=100))
        self.assertEqual(ordered_data[99], User.objects.get(id=1))
        
