"""
This module tests the behavior of the ``proxy.Proxy`` class.
"""
from firestone.handlers import BaseHandler
from firestone.authentication import DjangoAuthentication
from firestone.proxy import Proxy
from django.test import TestCase
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.models import User
from model_mommy import mommy
import json

class HandlerNoAuth(BaseHandler):
    authentication = None
    http_methods = ['get']

    def get(self, request, *args, **kwargs):
        return 'HandlerNoAuth'

class HandlerDjangoAuth(BaseHandler):    
    authentication = DjangoAuthentication
    http_methods = ['get']

    def get(self, request, *args, **kwargs):
        return 'HandlerDjangoAuth'

class TestProxy(TestCase):
    def test_does_it_initialize_the_correct_handlers(self):
        proxy = Proxy(HandlerNoAuth)
        self.assertEquals(proxy.handlers, (HandlerNoAuth,))

        proxy = Proxy(HandlerNoAuth, HandlerDjangoAuth)
        self.assertEquals(proxy.handlers, (HandlerNoAuth, HandlerDjangoAuth))
        
    def test_does_it_call_the_correct_handler(self):
        # Create proxy and non-authenticated request
        proxy = Proxy(HandlerNoAuth, HandlerDjangoAuth)
        request = RequestFactory().get('/')

        # Request is not authenticated, and anyway the ``HandlerNoAuth`` is
        # declared first in the Proxy creation, so it's always the one to get
        # called.
        self.assertIsInstance(proxy.choose_handler(request), HandlerNoAuth)
        
        # Create proxy and authenticate request
        proxy = Proxy(HandlerNoAuth, HandlerDjangoAuth)
        request.user = mommy.make(User)
        # Request is authenticated. However, ``HandlerNoAuth`` is
        # declared first in the Proxy creation, so it's always the one to get
        # called.
        self.assertIsInstance(proxy.choose_handler(request), HandlerNoAuth)



        # Create proxy and non-authenticated request
        proxy = Proxy(HandlerDjangoAuth, HandlerNoAuth)
        request = RequestFactory().get('whatever/')
        # Request is not authenticated and therefore will be carried out by
        # the ``HandlerNoAuth`` handler
        self.assertIsInstance(proxy.choose_handler(request), HandlerNoAuth)



        # Create proxy and authenticated request
        proxy = Proxy(HandlerDjangoAuth, HandlerNoAuth)
        request = RequestFactory().get('whatever')
        request.user = mommy.make(User)
        self.assertIsInstance(proxy.choose_handler(request), HandlerDjangoAuth)

    def test_does_it_return_403(self):
        """
        Does the proxy return a status code 403 when the handler demands some
        authentication, but the request is not authenticated?
        """
        proxy = Proxy(HandlerDjangoAuth)
        request = RequestFactory().get('whatever')
        self.assertEquals(proxy(request).status_code, 403)






        
