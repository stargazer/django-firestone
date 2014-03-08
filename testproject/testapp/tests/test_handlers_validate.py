"""
This module tests the ``firestone.handlers.ModelHandler.validate method
"""
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


class TestModelHandlerPOST(TestCase):
    def setUp(self):
        request = RequestFactory().post('/')
        handler = init_handler(ModelHandler(), request)
        handler.model = User
        self.handler = handler

    def test_dict(self):
        """
        ``request.data`` is a dictionary
        """
        handler = self.handler
        handler.request.data = {
            'username': 'user',
            'password': 'pass',
            'first_name': 'name',
        }                

        handler.validate()

        self.assertIsInstance(handler.request.data, handler.model)
        self.assertEqual(handler.request.data.username, 'user')
        self.assertEqual(handler.request.data.first_name, 'name')

    def test_dict_error(self):
        """
        ``request.data`` is a dictionary. 
        Mandatory parameters are missing
        """
        handler = self.handler

        handler.request.data = {
            'username': 'user',
            'first_name': 'name',
        }                

        self.assertRaises(
            exceptions.BadRequest,                
            handler.validate,
        )

    def test_list(self):
        """
        ``request.data`` is a list of dictionaries
        """
        handler = self.handler
        handler.request.data = [
            {
                'username': 'user0',
                'password': 'pass0',
                'first_name': 'name0',
            },
            {
                'username': 'user1',
                'password': 'pass1',
                'first_name': 'name1',
            },
            {
                'username': 'user2',
                'password': 'pass2',
                'first_name': 'name2',
            },
        ]

        handler.validate()

        self.assertEqual(len(handler.request.data), 3)
        for i in range(3):
            self.assertIsInstance(handler.request.data[i], handler.model)
            self.assertEqual(handler.request.data[i].username, 'user%s' % i)
            self.assertEqual(handler.request.data[i].first_name, 'name%s' % i)

    def test_list_error(self):
        """
        ``request.data`` is a list of dictionaries.
        Mandatory parameter missing from 2nd dictionary.
        """
        handler = self.handler
        handler.request.data = [
            {
                'username': 'user0',
                'password': 'pass0',
                'first_name': 'name0',
            },
            {
                'username': 'user1',
                'first_name': 'name1',
            },
            {
                'username': 'user2',
                'password': 'pass2',
                'first_name': 'name2',
            },
        ]

        self.assertRaises(
            exceptions.BadRequest,
            handler.validate,
        )


class TestModelHandlerPUT(TestCase):
    def setUp(self):
        request = RequestFactory().put('/')
        handler = init_handler(ModelHandler(), request)
        handler.model = User
        self.handler = handler

        mommy.make(User, 10)

    def test_single_model(self):
        """
        dataset is a single model instance
        """
        handler = self.handler
        handler.request.data = {
            'username': 'user',            
            'first_name': 'name',
        }                
        handler.kwargs = {'id': 1}

        handler.validate()
        self.assertIsInstance(handler.request.data, handler.model)
        self.assertEqual(handler.request.data.username, 'user')
        self.assertEqual(handler.request.data.first_name, 'name')         

    def test_single_model_error(self):
        """
        dataset is a single model instance. We set invalid field value
        """
        handler = self.handler
        handler.request.data = {'username': ''}
        handler.kwargs = {'id': 1}
        
        # Raises correct exception?
        self.assertRaises(
            exceptions.BadRequest,
            handler.validate,
        )

    def test_queryset(self):
        """
        dataset is a queryset
        """
        handler = self.handler
        handler.request.data = {
            'first_name': 'name',
            'last_name': 'surname',
        }

        handler.validate()
        for user in handler.request.data:
            self.assertIsInstance(user, handler.model)
            self.assertEqual(user.first_name, 'name')
            self.assertEqual(user.last_name, 'surname')

    def test_queryset_error(self):
        """
        dataset is a queryset. We set invalid field values
        """
        handler = self.handler
        handler.request.data = {'username': ''}
        handler.kwargs = {'id': 1}

        # Raises correct exception?
        self.assertRaises(
            exceptions.BadRequest,
            handler.validate,
        )
