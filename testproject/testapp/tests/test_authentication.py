"""
This module tests the behavior of the ``firestone.authentication`` module
"""
from firestone.authentication import NoAuthentication
from firestone.authentication import SessionAuthentication
from firestone.authentication import SignatureAuthentication
from django.test import TestCase
from django.test import RequestFactory
from django.contrib.auth.models import User
from model_mommy import mommy
import urllib


class TestNoAuthentication(TestCase):
    def test_authenticated(self):
        request = RequestFactory().get('/')
        auth = NoAuthentication()

        self.assertTrue(auth.is_authenticated(request))
        

class TestSessionAuthentication(TestCase):
    def test_not_authenticated(self):
        request = RequestFactory().get('/')
        auth = SessionAuthentication()

        self.assertFalse(auth.is_authenticated(request))

    def test_authenticated(self):
        request = RequestFactory().get('/')
        request.user = mommy.make(User)
        auth = SessionAuthentication()

        self.assertTrue(auth.is_authenticated(request))


class TestSignatureAuthentication(TestCase):
    """
    Testing the ``is_authenticated`` method, under different scenarios
    """
    def setUp(self):
        # Instance of SignatureAuthentication()
        self.auth = SignatureAuthentication()

        # Request characteristics
        self.method = 'POST'
        self.max_age = 60*60
        self.url = 'http://testserver/endpoint/'
        self.params = {'param1': 'value1', 'param2': 'value2'}
        
    def test_valid_signature(self):
        # Get signed url
        url = self.auth.get_signed_url(
           self.url, self.method, self.params, self.max_age  
        )              
        request = RequestFactory().post(url)
        
        # Is request valid?
        self.assertTrue(self.auth.is_authenticated(request))

    def test_missing_signature(self):
        # Update params dictionary, with signature and max_age        
        self.auth._update_params(
            self.url, self.method, self.params, self.max_age
        )
        # Remove signature
        del self.params[self.auth.sig_param]
        
        url = '%s?%s' % (self.url, urllib.urlencode(self.params))
        request = RequestFactory().post(url)
        # Is request valid?
        self.assertFalse(self.auth.is_authenticated(request))

    def test_tampered_signature(self):
        # Update params dictionary, with signature and max_age        
        self.auth._update_params(
            self.url, self.method, self.params, self.max_age
        )
        # Tamper signature
        self.params[self.auth.sig_param] += 'la'
        
        url = '%s?%s' % (self.url, urllib.urlencode(self.params))
        request = RequestFactory().post(url)
        # Is request valid?
        self.assertFalse(self.auth.is_authenticated(request))

    def test_tampered_querystring(self):
        self.auth._update_params(
            self.url, self.method, self.params, self.max_age
        )
        # Tamper querystring
        self.params['param1'] = 'tampered'
        
        url = '%s?%s' % (self.url, urllib.urlencode(self.params))
        request = RequestFactory().post(url)
        # Is request valid?
        self.assertFalse(self.auth.is_authenticated(request))

    def test_tampered_max_age(self):
        """
        The ``max_age`` parameter takes part to the signature computation, and
        therefore if tampered, the request's signature will not validate
        """
        self.auth._update_params(
            self.url, self.method, self.params, self.max_age
        )
        # Tamper max_age
        self.params[self.auth.max_age_param] += 1

        url = '%s?%s' % (self.url, urllib.urlencode(self.params))
        request = RequestFactory().post(url)
        # Is request valid?
        self.assertFalse(self.auth.is_authenticated(request))

    def test_expired_signature(self):
        self.auth._update_params(
            self.url, self.method, self.params, 0
        )
        
        url = '%s?%s' % (self.url, urllib.urlencode(self.params))
        request = RequestFactory().post(url)
        # Is request valid?
        self.assertFalse(self.auth.is_authenticated(request))

    def test_invalid_max_age(self):
        self.auth._update_params(
            self.url, self.method, self.params, 'invalid_max_age'
        )

        url = '%s?%s' % (self.url, urllib.urlencode(self.params))
        request = RequestFactory().post(url)
        # Is request valid?
        self.assertFalse(self.auth.is_authenticated(request))


