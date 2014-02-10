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

class TestBaseHandlerPut(TestCase):
    def test_put(self):
        handler = BaseHandler()       
        request = RequestFactory().put('/')

        self.assertRaises(
            exceptions.NotImplemented,
            handler.put,
            request
        )


class TestModelHandlerSinglePut(TestCase):
    def setUp(self):
        self.handler = ModelHandler()
        self.handler.model = User

        self.request = RequestFactory().put('/')
        self.user = mommy.make(User)
        self.user.username = 'other_username'
        self.request.data = self.user

    def test_ret_value(self):
        """
        Test returned value of put method
        """
        self.assertEqual(self.handler.put(self.request), self.user)

    def test_updated(self):
        """
        Test that the put method has indeed updated the model instance
        """
        res = self.handler.put(self.request)
        self.assertEqual(User.objects.get(id=res.id).username, 'other_username')

    def test_num_queries(self):
        """
        Test that only one DB query was performed
        """
        self.assertNumQueries(1, self.handler.put, self.request)

class TestModelHandlerPluralPut(TestCase):
    def setUp(self):
        self.handler = ModelHandler()
        self.handler.model = User

        self.request = RequestFactory().put('/')
        self.users = mommy.make(User, 10)
        for user in self.users:
            user.username = 'username%s' % user.id

        self.request.data = self.users            

    def test_ret_value(self):
        self.assertItemsEqual(self.handler.put(self.request), self.users)

    def test_updated(self):
        res = self.handler.put(self.request)
        for i in range(10):
            self.assertEqual(
                User.objects.get(id=i+1).username, 
                'username%s' % str(i + 1),
            )

    def test_num_queries(self):
        self.assertNumQueries(10, self.handler.put, self.request)


