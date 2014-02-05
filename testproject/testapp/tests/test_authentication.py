"""
This module tests the behavior of the ``firestone.authentication`` module
"""
from firestone.authentication import NoAuthentication
from firestone.authentication import DjangoAuthentication
from django.test import TestCase
from django.test import RequestFactory
from django.contrib.auth.models import User
from model_mommy import mommy


class TestNoAuthentication(TestCase):
    def test_authenticated(self):
        request = RequestFactory().get('/')
        auth = NoAuthentication()

        self.assertTrue(auth.is_authenticated(request))
        

class TestDjangoAuthentication(TestCase):
    def test_not_authenticated(self):
        request = RequestFactory().get('/')
        auth = DjangoAuthentication()

        self.assertFalse(auth.is_authenticated(request))

    def test_authenticated(self):
        request = RequestFactory().get('/')
        request.user = mommy.make(User)
        auth = DjangoAuthentication()

        self.assertTrue(auth.is_authenticated(request))
