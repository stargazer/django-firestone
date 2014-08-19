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
    def test_no_ordering(self):
        request = RequestFactory().get('/')
        handler = init_handler(BaseHandler(), request)

        data = 'whatever'
        self.assertEqual(
            handler.order(data),
            data
        )

    def test_ordering(self):
        request = RequestFactory().get('/?order=someorder')
        handler = init_handler(BaseHandler(), request)

        data = 'whatever'
        self.assertEqual(
            handler.order(data),
            data
        )

class TestModelHandlerOrder(TestCase):
    def setUp(self):
        mommy.make(User, 100)

    def test_no_ordering(self):
        request = RequestFactory().get('/')
        handler = init_handler(ModelHandler(), request)
        handler.model = User

        data = User.objects.all()
        self.assertEqual(
            handler.order(data),
            data,
        )

    def test_order_descending(self):
        def order_data(data, order):
            " Descending order"
            if order == 'id':
                return data.order_by('-id')
            return data
        
        request = RequestFactory().get('/?order=id')
        handler = init_handler(ModelHandler(), request)
        handler.model = User
        handler.order_data = order_data

        data = User.objects.all()
        ordered_data = handler.order(data)

        # Check if indeed the order of ``ordered_data`` is descending.
        self.assertEqual(ordered_data[0], User.objects.get(id=100))
        self.assertEqual(ordered_data[99], User.objects.get(id=1))
        
