"""
This module tests the behavior of the ``firestone.authentication`` module
"""
from firestone.authentication import NoAuthentication
from firestone.authentication import SessionAuthentication
from firestone.authentication import SignatureAuthentication
from firestone.authentication import JWTAuthentication
from oauth2_provider.models import AccessToken
from firestone.handlers import BaseHandler
from django.test import TestCase
from django.test import RequestFactory
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from model_mommy import mommy
import jwt
import datetime
import urllib


class HandlerNoAuth(BaseHandler):
    authentication = NoAuthentication

class HandlerSessionAuth(BaseHandler):
    authentication = SessionAuthentication

class HandlerSignatureAuth(BaseHandler):
    authentication = SignatureAuthentication

class HandlerJWTAuth(BaseHandler):
    authentication = JWTAuthentication

def init_handler(handler, request, *args, **kwargs):
    handler = handler()
    handler.request = request
    handler.args = args
    handler.kwargs = kwargs
    return handler




class TestNoAuthentication(TestCase):
    def test_authenticated(self):
        request = RequestFactory().get('/')
        handler = init_handler(HandlerNoAuth, request)

        self.assertTrue(handler.is_authenticated())
        

class TestSessionAuthentication(TestCase):
    def test_not_authenticated(self):
        request = RequestFactory().get('/')
        handler = init_handler(HandlerSessionAuth, request)

        self.assertFalse(handler.is_authenticated())

    def test_authenticated(self):
        request = RequestFactory().get('/')
        request.user = mommy.make(User)
        handler = init_handler(HandlerSessionAuth, request)

        self.assertTrue(handler.is_authenticated())


class TestSignatureAuthentication(TestCase):
    """
    Testing the ``is_authenticated`` method, under different scenarios
    """
    def setUp(self):
        # Request params
        self.method = 'POST'
        self.max_age = 60*60
        self.url = 'http://testserver/endpoint/'
        self.params = {'param1': 'value1', 'param2': 'value2'}
        
    def test_valid_signature(self):
        # Generate an initial handler, so that we can use methods from the
        # ``SignatureAuthentication`` mixin.
        url = '%s?%s' % (self.url, urllib.urlencode(self.params))
        request = RequestFactory().post(url)
        handler = init_handler(HandlerSignatureAuth, request)
        
        # Get signed url
        url = handler.get_signed_url(
           self.url, self.method, self.params, self.max_age  
        )              
        request = RequestFactory().post(url)
        handler = init_handler(HandlerSignatureAuth, request)

        # Is request valid?
        self.assertTrue(handler.is_authenticated())

    def test_missing_signature(self):
        # Generate an initial handler, so that we can use methods from the
        # ``SignatureAuthentication`` mixin.
        url = '%s?%s' % (self.url, urllib.urlencode(self.params))
        request = RequestFactory().post(url)
        handler = init_handler(HandlerSignatureAuth, request)
        
        # Update params dic with signature and max_age
        updated_params = handler._update_params(
            url, self.method, self.params, self.max_age
        )
        # remove signature from dictionary
        del updated_params[handler.sig_param]

        # Generate url 
        url = '%s?%s' % (self.url, urllib.urlencode(updated_params))
        request = RequestFactory().post(url)
        handler = init_handler(HandlerSignatureAuth, request)
        
        # Is request valid?
        self.assertFalse(handler.is_authenticated())

    def test_tampered_signature(self):
        # Generate an initial handler, so that we can use methods from the
        # ``SignatureAuthentication`` mixin.
        url = '%s?%s' % (self.url, urllib.urlencode(self.params))
        request = RequestFactory().post(url)
        handler = init_handler(HandlerSignatureAuth, request)
        
        # Update params dic with signature and max_age
        updated_params = handler._update_params(
            url, self.method, self.params, self.max_age
        )

        # Tamper signature
        updated_params[handler.sig_param] += 'lalala'

        # Generate url 
        url = '%s?%s' % (self.url, urllib.urlencode(updated_params))
        request = RequestFactory().post(url)
        handler = init_handler(HandlerSignatureAuth, request)
        
        # Is request valid?
        self.assertFalse(handler.is_authenticated())

    def test_tampered_querystring(self):
        # Generate an initial handler, so that we can use methods from the
        # ``SignatureAuthentication`` mixin.
        url = '%s?%s' % (self.url, urllib.urlencode(self.params))
        request = RequestFactory().post(url)
        handler = init_handler(HandlerSignatureAuth, request)
        
        # Update params dic with signature and max_age
        updated_params = handler._update_params(
            url, self.method, self.params, self.max_age
        )

        # Tamper querystring
        updated_params['param1'] = 'tampered'
        
        url = '%s?%s' % (self.url, urllib.urlencode(updated_params))
        request = RequestFactory().post(url)
        handler = init_handler(HandlerSignatureAuth, request)

        # Is request valid?
        self.assertFalse(handler.is_authenticated())

    def test_tampered_max_age(self):
        """
        The ``max_age`` parameter takes part to the signature computation, and
        therefore if tampered, the request's signature will not validate
        """
        # Generate an initial handler, so that we can use methods from the
        # ``SignatureAuthentication`` mixin.
        url = '%s?%s' % (self.url, urllib.urlencode(self.params))
        request = RequestFactory().post(url)
        handler = init_handler(HandlerSignatureAuth, request)
        
        # Update params dic with signature and max_age
        updated_params = handler._update_params(
            url, self.method, self.params, self.max_age
        )

        # Tamper max_age
        updated_params[handler.max_age_param] += 1

        url = '%s?%s' % (self.url, urllib.urlencode(updated_params))
        request = RequestFactory().post(url)
        handler = init_handler(HandlerSignatureAuth, request)

        # Is request valid?
        self.assertFalse(handler.is_authenticated())

    def test_expired_signature(self):
        # Generate an initial handler, so that we can use methods from the
        # ``SignatureAuthentication`` mixin.
        url = '%s?%s' % (self.url, urllib.urlencode(self.params))
        request = RequestFactory().post(url)
        handler = init_handler(HandlerSignatureAuth, request)
        
        # Update params dic with signature and max_age
        updated_params = handler._update_params(
            url, self.method, self.params, max_age=0
        )

        url = '%s?%s' % (self.url, urllib.urlencode(updated_params))
        request = RequestFactory().post(url)
        handler = init_handler(HandlerSignatureAuth, request)

        # Is request valid?
        self.assertFalse(handler.is_authenticated())

    def test_invalid_max_age(self):
        # Generate an initial handler, so that we can use methods from the
        # ``SignatureAuthentication`` mixin.
        url = '%s?%s' % (self.url, urllib.urlencode(self.params))
        request = RequestFactory().post(url)
        handler = init_handler(HandlerSignatureAuth, request)
        
        # Update params dic with signature and max_age
        updated_params = handler._update_params(
            url, self.method, self.params, max_age='invalid_max_age',
        )

        url = '%s?%s' % (self.url, urllib.urlencode(updated_params))
        request = RequestFactory().post(url)
        handler = init_handler(HandlerSignatureAuth, request)

        # Is request valid?
        self.assertFalse(handler.is_authenticated())


class TestJWTAuthentication(TestCase):
    def setUp(self):
        mommy.make(User, 10)

        # Generate a valid token
        payload = {
            'iss': 1,
            'iat': timezone.now(),
            'exp': timezone.now() + timedelta(days=1),
        }    
        self.token = jwt.encode(
            payload=payload, 
            key=settings.SECRET_KEY,
        )

    def test_valid_authorization_header(self):
        request = RequestFactory().get(
            '/', 
            HTTP_AUTHORIZATION='JWT %s' % self.token,
        )
        handler = init_handler(HandlerJWTAuth, request)

        self.assertTrue(handler.is_authenticated())

    def test_malformed_header_1(self):
        request = RequestFactory().get(
            '/',
            HTTP_AUTHORIZATION='%s' % self.token,
        )
        handler = init_handler(HandlerJWTAuth, request)

        self.assertFalse(handler.is_authenticated())

    def test_malformed_header_2(self):
        request = RequestFactory().get(
            '/',
            HTTP_AUTHORIZATION='Token %s' % self.token,
        )
        handler = init_handler(HandlerJWTAuth, request)

        self.assertFalse(handler.is_authenticated())

    def test_invalid_token_1(self):
        # modify a character off the encoded header
        self.token = self.token[1:]
        request = RequestFactory().get(
            '/',
            HTTP_AUTHORIZATION='JWT %s' % self.token,
        )
        handler = init_handler(HandlerJWTAuth, request)

        self.assertFalse(handler.is_authenticated())

    def test_invalid_token_2(self):
        # modify a character off the signature
        self.token = self.token[:-1]
        request = RequestFactory().get(
            '/',
            HTTP_AUTHORIZATION='JWT %s' % self.token,
        )
        handler = init_handler(HandlerJWTAuth, request)

        self.assertFalse(handler.is_authenticated())

    def test_no_user(self):
        # ``iss`` parameter does not exist
        payload = {'iat': timezone.now(), 'exp': timezone.now() + timedelta(days=1)}
        token = jwt.encode(
            payload=payload, 
            key=settings.SECRET_KEY,
        )

        request = RequestFactory().get(
            '/',
            HTTP_AUTHORIZATION='JWT %s' % token,
        )
        handler = init_handler(HandlerJWTAuth, request)

        self.assertFalse(handler.is_authenticated())



    def test_invalid_user(self):
        # Payload will refer to non-existing user
        # Generate a valid token
        payload = {'iss': 100, 'iat': timezone.now(), 'exp': timezone.now() + timedelta(days=1)}
        token = jwt.encode(
            payload=payload, 
            key=settings.SECRET_KEY,
        )

        request = RequestFactory().get(
            '/',
            HTTP_AUTHORIZATION='JWT %s' % token,
        )
        handler = init_handler(HandlerJWTAuth, request)

        self.assertFalse(handler.is_authenticated())

    def test_expired_token(self):
        payload = {'iss': 1, 'iat': timezone.now(), 'exp': timezone.now() - timedelta(days=10)}

        token = jwt.encode(
            payload=payload, 
            key=settings.SECRET_KEY,
        )
        request = RequestFactory().get(
            '/',
            HTTP_AUTHORIZATION='JWT %s' % token,
        )
        handler = init_handler(HandlerJWTAuth, request)

        self.assertFalse(handler.is_authenticated())

                



