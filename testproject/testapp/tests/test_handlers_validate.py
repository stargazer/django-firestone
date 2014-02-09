"""
This module tests the ``firestone.handlers.ModelHandler.validate method
"""
from firestone.handlers import ModelHandler
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
            'first_name': 'name',
        }                

        handler.validate(request)

        self.assertIsInstance(request.data, handler.model)
        self.assertEqual(request.data.username, 'user')
        self.assertEqual(request.data.first_name, 'name')

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
                'first_name': 'name0',
            },
            {
                'username': 'user1',
                'first_name': 'name1',
            },
            {
                'username': 'user2',
                'first_name': 'name2',
            },
        ]

        handler.validate(request)

        self.assertEqual(len(request.data), 3)
        for i in range(3):
            self.assertIsInstance(request.data[i], handler.model)
            self.assertEqual(request.data[i].username, 'user%s' % i)
            self.assertEqual(request.data[i].first_name, 'name%s' % i)

class TestModelHandlerPUT(TestCase):
    def test_1(self):
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
            
