"""
This module tests the
``firestone.handlers.HandlerControlFlow.authentication_hook`` method
"""
from firestone.handlers import BaseHandler
from firestone.authentication import SignatureAuthentication
from django.test import TestCase
from django.test import RequestFactory
from django.contrib.auth.models import User
from model_mommy import mommy


class TestAuthenticationHook(TestCase):
    def setUp(self):
        mommy.make(User, 10)
        self.handler = BaseHandler()
        self.handler.authentication = SignatureAuthentication()

        def authentication_hook(request, *args, **kwargs):
            # Sets ``request.user`` according to the ``user`` querystring param.
            request.user = User.objects.get(id=request.GET.get('user'))
        self.handler.authentication_hook = authentication_hook

    def test(self):
        request = RequestFactory().get('/?user=1')
        self.handler.authentication_hook(request)
        self.assertEqual(request.user, User.objects.get(id=1))



