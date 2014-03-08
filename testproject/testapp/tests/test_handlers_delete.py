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

def init_handler(handler, request, *args, **kwargs):
    # Mimicking the initialization of the handler instance
    handler.request = request
    handler.args = args
    handler.kwargs = kwargs
    return handler


class TestBaseHandlerDelete(TestCase):
    def test_delete(self):
        request = RequestFactory().delete('/')
        handler = init_handler(BaseHandler(), request)

        self.assertRaises(
            exceptions.NotImplemented,
            handler.delete,
        )

class TestModelHandlerSingularDelete(TestCase):
    def setUp(self):
        request = RequestFactory().delete('/')
        handler = init_handler(ModelHandler(), request)
        handler.model = User
        self.handler = handler

        self.user = mommy.make(User)

    def test_return_value(self):
        handler = self.handler
        handler.kwargs = {'id': self.user.id}
        self.assertEqual(
            handler.delete(), 
            self.user
        )

    def test_not_deleted(self):
        """
        Test that the data object has not been deleted yet
        """
        handler = self.handler
        handler.kwargs = {'id': self.user.id}
        handler.delete()
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
        handler = self.handler
        handler.kwargs = {'id': self.user.id}
        self.assertNumQueries(
            1,
            self.handler.delete,
        )

class TestModelHandlerPluralDelete(TestCase):
    def setUp(self):
        request = RequestFactory().delete('/')
        handler = init_handler(ModelHandler(), request)
        handler.model = User
        self.handler = handler

        mommy.make(User, 10)

    def test_return_value(self):
        handler = self.handler
        self.assertItemsEqual(
            handler.delete(),
            User.objects.all(),
        )                

    def test_not_deleted(self):
        handler = self.handler
        handler.delete()
        self.assertEqual(
            User.objects.count(),
            10,
        )            

    def test_num_queries(self):
        """
        Here, no query should be executed. Not even the one retrieving the
        data, since it returns a QuerySet, which is a lazy data structure.
        """
        handler = self.handler
        self.assertNumQueries(
            0,
            handler.delete,
        )
