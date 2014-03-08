"""
This module tests the ``firestone.handler.BaseHandler.order_data`` method
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


class TestBaseHandlerOrderData(TestCase):
    def test_order_data(self):
        request = RequestFactory().get('/')
        handler = init_handler(BaseHandler(), request)
        data = 'data'
        order = 'someorder'

        self.assertEqual(
            handler.order_data(data, order),
            data
        )

class TestModelHandlerOrderData(TestCase):
    def setUp(self):
        request = RequestFactory().get('/')
        handler = init_handler(ModelHandler(), request)
        handler.model = User
        self.handler = handler
        
        mommy.make(User, 100)

    def test_order_data_plural(self):
        handler = self.handler
        data = User.objects.all()
        order = 'someorder'

        self.assertEqual(
            handler.order_data(data, order),
            data,
        )

    def test_order_data_singular(self):
        # Thing is that ``order_data`` is called by ``get_data_set``. So it's
        # never the case that it's called with ``data`` being a single model
        # instance. However, I just test here for clarity.
        handler = self.handler
        data = User.objects.get(id=1)
        order = 'someorder'

        self.assertEqual(
            handler.order_data(data, order),
            data,
        )


