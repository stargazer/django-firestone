"""
This module tests the ``firestone.handlers.BaseHandler.delete`` and
``firestone.handlers.ModelHandler.delete`` methods.
"""
from firestone.handlers import BaseHandler
from firestone.handlers import ModelHandler
from firestone import exceptions
from django.test import TestCase
from django.test import RequestFactory
from django.contrib.auth.models import User
from model_mommy import mommy

class TestBaseHandlerDelete(TestCase):
    def test_delete(self):
        handler = BaseHandler()
        request = RequestFactory().delete('/')

        self.assertRaises(
            exceptions.NotImplemented,
            handler.delete,
            request
        )

class TestModelHandlerSingularDelete(TestCase):
    def setUp(self):
        self.handler = ModelHandler()
        self.handler.model = User

        self.request = RequestFactory().delete('/')
        self.user = mommy.make(User)

    def test_return_value(self):
        self.assertEqual(
            self.handler.delete(self.request, id=self.user.id), 
            self.user
        )

    def test_not_deleted(self):
        """
        Test that the data object has not been deleted yet
        """
        self.handler.delete(self.request, id=self.user.id)
        try:
            User.objects.get(id=self.user.id)
        except User.DoesNotExist:
            assert(False)
        else:
            assert True

    def test_num_queries(self):
        """
        The only query that has been executed, is a SELECT for retrieving the
        data item.
        """
        self.assertNumQueries(
            1,
            self.handler.delete,
            self.request, id=self.user.id
        )

class TestModelHandlerPluralDelete(TestCase):
    def setUp(self):
        self.handler = ModelHandler()
        self.handler.model = User
        self.request = RequestFactory().delete('/')

        mommy.make(User, 10)

    def test_return_value(self):
        self.assertItemsEqual(
            self.handler.delete(self.request),
            User.objects.all(),
        )                

    def test_not_deleted(self):
        self.handler.delete(self.request)
        self.assertEqual(
            User.objects.count(),
            10,
        )            

    def test_num_queries(self):
        """
        Here, no query should be executed. Not even the one retrieving the
        data, since it returns a QuerySet, which is a lazy data structure.
        """
        self.assertNumQueries(
            0,
            self.handler.delete,
            self.request
        )
