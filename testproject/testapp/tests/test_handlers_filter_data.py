"""
This module tests the ``firestone.handlers.BaseHandler.filters`` parameter and
its behavior.
"""
from firestone.handlers import BaseHandler
from firestone.handlers import ModelHandler
from django.test import TestCase
from django.test import RequestFactory
from django.contrib.auth.models import User
from model_mommy import mommy
import string
import random


class TestModelHandler(TestCase):
    def setUp(self):
        # Initialize data
        self.users = mommy.make(User, 100)
        for user in User.objects.all():
            user.first_name = ''.join([random.choice(string.ascii_uppercase) for i in range(5)])
            user.email = ''.join([random.choice(string.ascii_uppercase) for i in range(10)])
            user.save()

        # Initialize handler
        handler = ModelHandler()
        handler.model = User
        handler.filters = (
            'filter_id', 
            'filter_name',
            'filter_email',
        )
        def filter_id(data, request, *args, **kwargs):
            ids = request.GET.getlist('id')
            if ids:
                data = data.filter(id__in=ids)
            return data
        handler.filter_id = filter_id

        def filter_name(data, request, *args, **kwargs):
            names = request.GET.getlist('name')
            if names:
                data = data.filter(first_name__in=names)
            return data
        handler.filter_name = filter_name

        def filter_email(data, request, *args, **kwargs):
            emails = request.GET.getlist('email')
            if emails:
                data = data.filter(email__in=emails)
            return data
        handler.filter_email = filter_email

        self.handler = handler

    def test_no_filters(self):
        """ Requests don't apply filtering """
        handler = self.handler
        request = RequestFactory().get('/')
        data = User.objects.all()

        self.assertItemsEqual(
            handler.filter_data(data, request),
            self.users,
        )

    def test_one_filter(self):
        """ Requests apply one single filter each """
        handler = self.handler
        data = User.objects.all()
        
        # id filter
        request = RequestFactory().get('/?id=1&id=2&id=3&id=4&id=5')
        self.assertItemsEqual(
            handler.filter_data(data, request),
            User.objects.filter(id__lte=5),
        )

        # name filter 
        data = User.objects.all()
        names = tuple([user.first_name for user in User.objects.filter(id__lte=10)])
        request = RequestFactory().get('/?' + 'name=%s&'*10 % names)
        self.assertItemsEqual(
            handler.filter_data(data, request),
            User.objects.filter(id__lte=10),
        )

        # email filter
        data = User.objects.all()
        emails = tuple([user.email for user in User.objects.filter(id__lte=15)])
        request = RequestFactory().get('/?' + 'email=%s&'*15 % emails)
        self.assertItemsEqual(
            handler.filter_data(data, request),
            User.objects.filter(id__lte=15),
        )

    def test_two_filters(self):
        handler = self.handler
        data = User.objects.all()

        # id  & name filter
        name1 = User.objects.get(id=1).first_name
        name2 = User.objects.get(id=2).first_name
        request = RequestFactory().get('/?id=1&id=2&id=3&id=4&id=5&name=%s&name=%s' % (name1, name2))
        self.assertItemsEqual(
            handler.filter_data(data, request),
            User.objects.filter(id__lte=2),
        )

    def test_three_filters(self):
        handler = self.handler

        # id & name & email filter. End up selecting 1 item
        data = User.objects.all()
        name1 = User.objects.get(id=1).first_name
        name2 = User.objects.get(id=2).first_name
        email = User.objects.get(id=1).email

        request = RequestFactory().get('/?id=1&id=2&id=3&id=4&id=5&name=%s&name=%s&email=%s' % (name1, name2, email))
        self.assertItemsEqual(
            handler.filter_data(data, request),
            User.objects.filter(id=1),
        )

        # id & name & email filter. End up selecting 0 items
        data = User.objects.all()
        name1 = User.objects.get(id=1).first_name
        name2 = User.objects.get(id=2).first_name
        email = User.objects.get(id=100).email

        request = RequestFactory().get('/?id=1&id=2&id=3&id=4&id=5&name=%s&name=%s&email=%s' % (name1, name2, email))
        self.assertItemsEqual(
            handler.filter_data(data, request),
            [],
        )

