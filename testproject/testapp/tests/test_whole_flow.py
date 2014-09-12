"""
This module tests the whole data flow of API handlers
"""
from firestone.proxy import Proxy
from firestone.handlers import BaseHandler
from firestone.handlers import ModelHandler
from firestone.authentication import SessionAuthentication
from firestone.authentication import JWTAuthentication
from django.contrib.auth.models import User
from django.test import TestCase
from django.test import RequestFactory
from django.utils import timezone
from django.conf import settings
from model_mommy import mommy
from random import randint
from datetime import timedelta
import json
from itsdangerous import TimedJSONWebSignatureSerializer
               

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



class ModelHandlerExample(ModelHandler):
    authentication = JWTAuthentication
    model = User
    http_methods = ['GET', 'POST', 'DELETE']
    post_body_fields = ['first_name', 'last_name', 'username', 'password']
    filters = ('filter_id',)

    content_type_template = {
        'fields': ['id', ],
        'flat': False,
    }            
    logentry_template = {
        'fields': ['action_flag', 'content_type'],     
        'related': {
            'content_type': content_type_template,
        }
    }
    template = {
        'fields': ['id', 'username', 'first_name', 'last_name',
                   'logentry_set', 'email', 'last_login', 'nickname'], 
        'related': {
            'logentry_set': logentry_template,
        }, 
        'exclude': ['password', 'date_joined',],
        'allow_missing': True,
    }

    def working_set(self):
        # I don't override the method, so that the user will get access to all
        # users :-)
        return super(ModelHandlerExample, self).working_set()

    def filter_id(self, data):
        ids = self.request.GET.getlist('id')
        if ids:
            data = User.objects.filter(id__in=ids)            
        return data            

    def order_data(self, data, order):
        if order == 'username':
            return data.order_by('username')
        
        return data
modelhandler_proxy = Proxy(ModelHandlerExample)
    

class TestModelHandler(TestCase):
    def setUp(self):
        mommy.make(User, 10)

        s = TimedJSONWebSignatureSerializer(
            settings.SECRET_KEY, 
            expires_in=3600*24
        )
        self.token = s.dumps({'iss':1})

    def test_not_authenticated(self):
        # request is not authenticated
        request = RequestFactory().get('')
        response = modelhandler_proxy(request)

        self.assertEqual(response.status_code, 403)

    def test_get_singular(self):
        # singular, authenticated request
        request = RequestFactory().get(
            '', 
            HTTP_AUTHORIZATION='JWT %s' % self.token
        )
        kwargs = {'id': 5}
        
        response = modelhandler_proxy(request, **kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json; charset=utf-8')
        
        content = json.loads(response.content)['data']
        self.assertIsInstance(content, dict)
        self.assertEqual(content['id'], 5)

    def test_get_plural(self):
        # plural authenticated request
        request = RequestFactory().get(
            '', 
            HTTP_AUTHORIZATION='JWT %s' % self.token
        )
        
        response = modelhandler_proxy(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json; charset=utf-8')
        
        content = json.loads(response.content)['data']
        self.assertIsInstance(content, list)
        self.assertEquals(len(content), 10)
        
        # If ordering is the default, by id
        user_ids = [user['id'] for user in content]
        self.assertItemsEqual(user_ids, range(1, 11))

    def test_get_plural_filter_id(self):
        request = RequestFactory().get(
            '?id=1&id=2&id=3', 
            HTTP_AUTHORIZATION='JWT %s' % self.token
        )
        
        response = modelhandler_proxy(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json; charset=utf-8')
        
        content = json.loads(response.content)['data']
        self.assertIsInstance(content, list)
        self.assertEquals(len(content), 3)

        # If only the correct items have been returned
        user_ids = [user['id'] for user in content]
        self.assertItemsEqual(user_ids, [user.id for user in User.objects.filter(id__lt=4)])

    def test_get_plural_order_username(self):
        request = RequestFactory().get(
            '?order=first_name', 
            HTTP_AUTHORIZATION='JWT %s' % self.token
        )
                
        response = modelhandler_proxy(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json; charset=utf-8')
        
        content = json.loads(response.content)['data']
        self.assertIsInstance(content, list)
        self.assertEquals(len(content), 10)
        
        # If ordering is correct
        user_ids = [user['id'] for user in content]
        self.assertItemsEqual(user_ids, [user.id for user in User.objects.order_by('username')])

    def test_post_missing_field(self):
        # missing ``username`` and ``password`` field. Should return status code 400
        request = RequestFactory().post(
            '/',
            data=json.dumps({'first_name': 'name', 'last_name': 'surname'}),
            content_type='application/json',           
            HTTP_AUTHORIZATION='JWT %s' % self.token
        )
                
        response = modelhandler_proxy(request)
        self.assertEqual(response.status_code, 400)

    def test_post_valid(self):
        request = RequestFactory().post(
            '/',
            data=json.dumps({
                'first_name': 'name', 'last_name': 'surname',
                'username': 'username', 'password': 'password',
            }),
            content_type='application/json',           
            HTTP_AUTHORIZATION='JWT %s' % self.token
        )
                
        response = modelhandler_proxy(request)
        self.assertEqual(response.status_code, 200)


    def test_delete_singular(self):
        request = RequestFactory().delete(
            '',
            HTTP_AUTHORIZATION='JWT %s' % self.token
        )
        kwargs = {'id': 5}

        response = modelhandler_proxy(request, **kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json; charset=utf-8')
        
        content = json.loads(response.content)['data']
        self.assertIsInstance(content, dict)
        self.assertEqual(content['id'], 5)

    def test_delete_plural(self):
        # Should not be allowed
        request = RequestFactory().delete(
            '',
            HTTP_AUTHORIZATION='JWT %s' % self.token
        )

        response = modelhandler_proxy(request)
        self.assertEqual(response.status_code, 405)

    def test_put(self):
        # Should not be allowed
        request = RequestFactory().put(
            '',                
            HTTP_AUTHORIZATION='JWT %s' % self.token
        )
        response = modelhandler_proxy(request)
        self.assertEqual(response.status_code, 405)

