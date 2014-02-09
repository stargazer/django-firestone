"""
This module tests the ``firestone.handlers.ModelHandler.validate method
"""
from firestone.handlers import ModelHandler
from firestone import exceptions
from django.test import TestCase
from django.test import RequestFactory
from django.contrib.auth.models import User
from model_mommy import mommy


class TestModelHandlerPOST(TestCase):
    def test_dict(self):
        """
        ``request.data`` is a dictionary
        """
        handler = ModelHandler()
        handler.model = User

        request = RequestFactory().post('/')
        request.data = {
            'username': 'user',
            'password': 'pass',
            'first_name': 'name',
        }                

        handler.validate(request)

        self.assertIsInstance(request.data, handler.model)
        self.assertEqual(request.data.username, 'user')
        self.assertEqual(request.data.first_name, 'name')

    def test_dict_error(self):
        """
        ``request.data`` is a dictionary. 
        Mandatory parameters are missing
        """
        handler = ModelHandler()
        handler.model = User

        request = RequestFactory().post('/')
        request.data = {
            'username': 'user',
            'first_name': 'name',
        }                

        self.assertRaises(
            exceptions.BadRequest,                
            handler.validate,
            request
        )

    def test_list(self):
        """
        ``request.data`` is a list of dictionaries
        """
        handler = ModelHandler()
        handler.model = User

        request = RequestFactory().post('/')
        request.data = [
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

        handler.validate(request)

        self.assertEqual(len(request.data), 3)
        for i in range(3):
            self.assertIsInstance(request.data[i], handler.model)
            self.assertEqual(request.data[i].username, 'user%s' % i)
            self.assertEqual(request.data[i].first_name, 'name%s' % i)

    def test_list_error(self):
        """
        ``request.data`` is a list of dictionaries.
        Mandatory parameter missing from 2nd dictionary.
        """
        handler = ModelHandler()
        handler.model = User

        request = RequestFactory().post('/')
        request.data = [
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
            request
        )


class TestModelHandlerPUT(TestCase):
    def test_single_model(self):
        """
        dataset is a single model instance
        """
        handler = ModelHandler()
        handler.model = User

        mommy.make(User, 10)
        
        request = RequestFactory().put('/')
        request.data = {
            'username': 'user',            
            'first_name': 'name',
        }                

        handler.validate(request, id=1)

        self.assertIsInstance(request.data, handler.model)
        self.assertEqual(request.data.username, 'user')
        self.assertEqual(request.data.first_name, 'name')         

    def test_single_model_error(self):
        """
        dataset is a single model instance. We set invalid field value
        """
        handler = ModelHandler()
        handler.model = User
        
        mommy.make(User, 10)
        request = RequestFactory().put('/')
        request.data = {'username': ''}

        # Raises correct exception?
        self.assertRaises(
            exceptions.BadRequest,
            handler.validate,
            request,
            id=1,
        )

    def test_queryset(self):
        """
        dataset is a queryset
        """
        handler = ModelHandler()
        handler.model = User

        mommy.make(User, 10)

        request = RequestFactory().put('/')
        request.data = {
            'first_name': 'name',
            'last_name': 'surname',
        }

        handler.validate(request)

        for user in request.data:
            self.assertIsInstance(user, handler.model)
            self.assertEqual(user.first_name, 'name')
            self.assertEqual(user.last_name, 'surname')

    def test_queryset_error(self):
        """
        dataset is a queryset. We set invalid field values
        """
        handler = ModelHandler()
        handler.model = User

        mommy.make(User, 10)

        request = RequestFactory().put('/')
        request.data = {'username': ''}

        # Raises correct exception?
        self.assertRaises(
            exceptions.BadRequest,
            handler.validate,
            request,
            id=1,
        )
