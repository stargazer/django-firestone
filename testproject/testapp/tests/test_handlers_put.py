"""
This module tests ``firestone.handlers.BaseHandler.put`` and
``firestone.handlers.ModelHandler.put`` methods.
"""
from firestone.handlers import BaseHandler
from firestone.handlers import ModelHandler
from firestone import exceptions
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


class TestBaseHandlerPut(TestCase):
    def test_put(self):
        request = RequestFactory().put('/')
        handler = init_handler(BaseHandler(), request)

        self.assertRaises(
            exceptions.NotImplemented,
            handler.put,
        )


class TestModelHandlerSinglePut(TestCase):
    def setUp(self):
        request = RequestFactory().put('/')
        handler = init_handler(ModelHandler(), request)
        handler.model = User
        self.handler = handler

        self.user = mommy.make(User)
        self.user.username = 'other_username'
        self.handler.request.data = self.user

    def test_ret_value(self):
        """
        Test returned value of put method
        """
        self.assertEqual(self.handler.put(), self.user)

    def test_updated(self):
        """
        Test that the put method has indeed updated the model instance
        """
        res = self.handler.put()
        self.assertEqual(User.objects.get(id=res.id).username, 'other_username')

    def test_num_queries(self):
        """
        Test that only one DB query was performed
        """
        self.assertNumQueries(1, self.handler.put)


class TestModelHandlerPluralPut(TestCase):
    def setUp(self):
        request = RequestFactory().put('/')
        handler = init_handler(ModelHandler(), request)
        handler.model = User
        self.handler = handler

        self.users = mommy.make(User, 10)
        for user in self.users:
            user.username = 'username%s' % user.id

        self.handler.request.data = self.users            

    def test_ret_value(self):
        self.assertItemsEqual(self.handler.put(), self.users)

    def test_updated(self):
        res = self.handler.put()
        for i in range(10):
            self.assertEqual(
                User.objects.get(id=i+1).username, 
                'username%s' % str(i + 1),
            )

    def test_num_queries(self):
        self.assertNumQueries(10, self.handler.put)


