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

def init_handler(handler, request, *args, **kwargs):
    # Mimicking the initialization of the handler instance
    handler.request = request
    handler.args = args
    handler.kwargs = kwargs
    return handler


class TestBaseHandlerGet(TestCase):
    def setUp(self):
        request = RequestFactory().get('/')
        handler = init_handler(BaseHandler(), request)
        self.handler = handler

    def test_plural(self):
        handler = self.handler

        self.assertRaises(
            exceptions.NotImplemented,
            handler.get,
        )

    def test_singular(self):
        handler = self.handler
        handler.kwargs = {'id': 1}

        self.assertRaises(
            exceptions.NotImplemented,
            handler.get,
        )

class TestModelHandlerGetSingular(TestCase):
    def setUp(self):
        request = RequestFactory().get('/')
        handler = init_handler(ModelHandler(), request)
        handler.model = User
        self.handler = handler

        mommy.make(User, 10)

    def test_singular_exists(self):
        """
        Test result
        """
        handler = self.handler
        handler.kwargs = {'id': 1}
        self.assertEqual(
            handler.get(), 
            User.objects.get(id=1)
        )

        handler.kwargs = {'id': 10}
        self.assertEqual(
            self.handler.get(),
            User.objects.get(id=10)
        )

    def test_singular_exists_num_queries(self):
        """
        Test num queries
        """
        handler = self.handler
        handler.kwargs = {'id': 1}
        self.assertNumQueries(
            1,
            handler.get,
        )

        handler.kwargs = {'id': 10}
        self.assertNumQueries(
            1,
            handler.get,
        )

    def test_singular_doesnt_exist(self):
        handler = self.handler
        handler.kwargs = {'id': 1000}
        self.assertRaises(
            exceptions.Gone,
            handler.get,
        )

        handler.kwargs = {'id': 1000000}
        self.assertRaises(
            exceptions.Gone,
            handler.get,
        )

    def test_singular_invalid_type(self):
        handler = self.handler
        handler.kwargs = {'id': 'string'}
        self.assertRaises(
            exceptions.Gone,
            handler.get,
        )

        handler.kwargs = {'id': {'key': 'value'}}
        self.assertRaises(
            exceptions.Gone,
            handler.get,
        )



class TestModelHandlerGetPlural(TestCase):
    def setUp(self):
        request = RequestFactory().get('/')
        handler = init_handler(ModelHandler(), request)
        handler.model = User
        self.handler = handler

        mommy.make(User, 10)

    def test_plural(self):
        handler = self.handler
        self.assertItemsEqual(
            handler.get(), 
            User.objects.all()
        )

    def test_plural_num_queries(self):
        handler = self.handler
        self.assertNumQueries(
            0,
            handler.get,
        )
        # Note: Why does a plural result in 0 queries, whereas singular results
        # in 1 query? 
        # Querysets are lazy, and don't hit the db unless we try to access
        # their results.
        # Singular requests though perform a ``get`` on the Queryset result,
        # which results in one query.
