"""
This module tests the whole data flow of API handlers
"""
from firestone.proxy import Proxy
from firestone.handlers import BaseHandler
from firestone.handlers import ModelHandler
from firestone.authentication import SessionAuthentication
from django.contrib.auth.models import User
from django.test import TestCase
from django.test import RequestFactory
from model_mommy import mommy
from random import randint
import json


class BaseHandlerExample(BaseHandler):
    authentication = SessionAuthentication
    http_methods = ['GET',]
    template = {
        'fields': ['id', 'map', 'array']
    }

    def get(self):
        return self.get_data()

    def get_data_item(self):
        # If ``id`` in ``kwargs``, returns a single dictionary
        id = self.kwargs.get('id')
        if id:
            return {
                'id': id,
                'map': {
                    'key1': randint(1, 100),
                    'key2': randint(1, 100),
                 },
                'array': [randint(1, 100) for i in range(randint(1, 10))]
            }                    

    def get_data_set(self):
        # Returns a list of dictionaries
        data = []
        for id in range(randint(1, 100)):    
             data.append({            
                'id': id,
                'map': {
                    'key1': randint(1, 100),
                    'key2': randint(1, 100),
                 },
                'array': [randint(1, 100) for i in range(randint(1, 10))]
        
            })
        return data                
basehandler_proxy = Proxy(BaseHandlerExample)


class TestBaseHandler(TestCase):
    def setUp(self):
        mommy.make(User, 10)

    def test_not_authenticated(self):
        # request is not authenticated
        request = RequestFactory().get('')
        response = basehandler_proxy(request)

        self.assertEqual(response.status_code, 403)

    def test_get_singular(self):
        # singular, authenticated request

        request = RequestFactory().get('')
        request.user = User.objects.get(id=1)   # authenticate
        kwargs = {'id': 15}
        
        response = basehandler_proxy(request, **kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json; charset=utf-8')
        
        content = json.loads(response.content)['data']
        self.assertIsInstance(content, dict)
        self.assertIsInstance(content['id'], int)
        self.assertIsInstance(content['map'], dict)
        self.assertIsInstance(content['array'], list)

    def test_get_plural(self):
        # plural authenticated request

        request = RequestFactory().get('')
        request.user = User.objects.get(id=1)   # authenticate

        response = basehandler_proxy(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json; charset=utf-8')
        
        content = json.loads(response.content)['data']
        self.assertIsInstance(content, list)

    def test_get_post(self):
        # post request should fail

        request = RequestFactory().post('')
        request.user = User.objects.get(id=1)

        response = basehandler_proxy(request)
        self.assertEqual(response.status_code, 405)


