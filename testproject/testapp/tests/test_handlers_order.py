"""
This module tests the ``firestone.handlers.BaseHandler.order`` method
"""
from firestone.handlers import BaseHandler
from firestone.handlers import ModelHandler
from django.test import TestCase
from django.test import RequestFactory
from django.contrib.auth.models import User
from model_mommy import mommy


class TestBaseHandlerOrder(TestCase):
    def test_no_ordering(self):
        handler = BaseHandler()
        request = RequestFactory().get('/')
        data = 'whatever'

        self.assertEqual(
            handler.order(data, request),
            data
        )

    def test_ordering(self):
        handler = BaseHandler()
        request = RequestFactory().get('/?order=someordering')
        data = 'whatever'

        self.assertEqual(
            handler.order(data, request),
            data
        )

class TestModelHandlerOrder(TestCase):
    def setUp(self):
        mommy.make(User, 100)
        self.handler = ModelHandler()
        self.handler.model = User
        self.request = RequestFactory().get('/')

    def test_order_default(self):
        data = User.objects.all()
        self.assertEqual(
            self.handler.order(data, self.request),
            data,
        )

    def test_order_descending(self):
        def order(data, request, *args, **kwargs):
            " Descending order"
            return data.order_by('-id')
        self.handler.order = order

        data = User.objects.all()
        ordered_data = self.handler.order(data, self.request)

        # Check if indeed the order of ``ordered_data`` is descending.
        self.assertEqual(ordered_data[0], User.objects.get(id=100))
        self.assertEqual(ordered_data[99], User.objects.get(id=1))
        
