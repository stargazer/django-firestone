"""
This module tests the behavior of the ``views.View`` proxy view.
"""
from firestone.handlers import BaseHandler
from firestone.authentication import DjangoAuthentication
from firestone.views import View
from django.test import TestCase
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.models import User
from model_mommy import mommy

class HandlerNoAuth(BaseHandler):
    authentication = None
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        return 'HandlerNoAuth'

class HandlerDjangoAuth(BaseHandler):    
    authentication = DjangoAuthentication
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        return 'HandlerDjangoAuth'

class TestView(TestCase):
    def test_does_it_initialize_the_correct_handlers(self):
        view = View(HandlerNoAuth)
        self.assertEquals(view.handlers, (HandlerNoAuth,))

        view = View(HandlerNoAuth, HandlerDjangoAuth)
        self.assertEquals(view.handlers, (HandlerNoAuth, HandlerDjangoAuth))
        
    def test_does_it_call_the_correct_handler(self):
        # Create view and non-authenticated request
        view = View(HandlerNoAuth, HandlerDjangoAuth)
        request = RequestFactory().get('whatever/')
        
        # Request is not authenticated, and anyway the ``HandlerNoAuth`` is
        # declared first in the View creation, so it's always the one to get
        # called.
        self.assertEquals(view(request).content, 'HandlerNoAuth')


        # Create view and authenticate request
        view = View(HandlerNoAuth, HandlerDjangoAuth)
        request.user = mommy.make(User)

        # Request is authenticated. However, ``HandlerNoAuth`` is
        # declared first in the View creation, so it's always the one to get
        # called.
        self.assertEquals(view(request).content, 'HandlerNoAuth')



        # Create view and non-authenticated request
        view = View(HandlerDjangoAuth, HandlerNoAuth)
        request = RequestFactory().get('whatever/')
        # Request is not authenticated and therefore will be carried out by
        # the ``HandlerNoAuth`` handler
        self.assertEquals(view(request).content, 'HandlerNoAuth')



        # Create view and authenticated request
        view = View(HandlerDjangoAuth, HandlerNoAuth)
        request = RequestFactory().get('whatever')
        request.user = mommy.make(User)
        self.assertEquals(view(request).content, 'HandlerDjangoAuth')

    def test_does_it_return_403(self):
        """
        Does the view return a status code 403 when the handler demands some
        authentication, but the request is not authenticated?
        """
        view = View(HandlerDjangoAuth)
        request = RequestFactory().get('whatever')
        self.assertEquals(view(request).status_code, 403)






        
