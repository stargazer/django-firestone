"""
This module tests the ``firestone.handlers.BaseHandler.get`` and
``firestone.handlers.ModelHandler.get`` methods
"""
from django.test import TestCase
from django.test import RequestFactory
from django.contrib.auth.models import User
from firestone.handlers import BaseHandler
from firestone.handlers import ModelHandler
from firestone import exceptions
from model_mommy import mommy

class TestBaseHandlerGet(TestCase):
    def test_plural(self):
        handler = BaseHandler()            
        request = RequestFactory().get('/')

        self.assertRaises(
            exceptions.NotImplemented,
            handler.get,
            request,
        )

    def test_singular(self):
        handler = BaseHandler()            
        request = RequestFactory().get('/')

        self.assertRaises(
            exceptions.NotImplemented,
            handler.get,
            request, id=1,
        )

class TestModelHandlerGetSingular(TestCase):
    def setUp(self):
        self.handler = ModelHandler()
        self.handler.model = User
        self.request = RequestFactory().get('/')
        mommy.make(User, 10)

    def test_singular_exists(self):
        """
        Test result
        """
        self.assertEqual(
            self.handler.get(self.request, id=1), 
            User.objects.get(id=1)
        )
        self.assertEqual(
            self.handler.get(self.request, id=10),
            User.objects.get(id=10)
        )

    def test_singular_exists_num_queries(self):
        """
        Test num queries
        """
        self.assertNumQueries(
            1,
            self.handler.get,
            self.request, id=1,
        )

        self.assertNumQueries(
            1,
            self.handler.get,
            self.request, id=10,
        )

    def test_singular_doesnt_exist(self):
        self.assertRaises(
            exceptions.Gone,
            self.handler.get,
            self.request, id=1000,
        )

        self.assertRaises(
            exceptions.Gone,
            self.handler.get,
            self.request, id=100000,
        )

    def test_singular_invalid_type(self):
        self.assertRaises(
            exceptions.Gone,
            self.handler.get,
            self.request, id='string',
        )
        self.assertRaises(
            exceptions.Gone,
            self.handler.get,
            self.request, id={'key': 'value'},
        )



class TestModelHandlerGetPlural(TestCase):
    def setUp(self):
        self.handler = ModelHandler()
        self.handler.model = User
        self.request = RequestFactory().get('/')
        mommy.make(User, 10)

    def test_plural(self):
        self.assertItemsEqual(
            self.handler.get(self.request), 
            User.objects.all()
        )

    def test_plural_num_queries(self):
        self.assertNumQueries(
            0,
            self.handler.get,
            self.request,
        )
        # Note: Why does a plural result in 0 queries, whereas singular results
        # in 1 query? 
        # Querysets are lazy, and don't hit the db unless we try to access
        # their results.
        # Singular requests though perform a ``get`` on the Queryset result,
        # which results in one query.
