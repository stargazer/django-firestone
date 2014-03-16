"""
This module tests the method ``firestone.handlers.HandlerControlFlow.inject_data_hook``
"""
from firestone.handlers import BaseHandler
from django.contrib.auth.models import User
from django.test import TestCase
from django.test import RequestFactory
from model_mommy import mommy


class TestInjectDataHook(TestCase):
    def setUp(self):
        mommy.make(User, 10)
        self.handler = BaseHandler()

    def test(self):
        request = RequestFactory().get('/')
        data = User.objects.all()
        self.assertItemsEqual(
            self.handler.inject_data_hook(data),
            data,
        )



