"""
This module tests the ``firestone.handlers.BaseHandler.slice`` and
``firestone.handlers.ModelHandler.slice`` methods.
"""
from firestone.handlers import BaseHandler
from firestone.handlers import ModelHandler
from firestone import exceptions
from django.test import TestCase
from django.test import RequestFactory
from django.contrib.auth.models import User
from model_mommy import mommy


class TestBaseHandlerSlice(TestCase):
    def test_slice(self):
        handler = BaseHandler()
        request = RequestFactory().get('/')
        data = 'whatever'
        self.assertEqual(
            handler.slice(data, request), 
            (data, None) 
        )

class TestModelHandlerSlice(TestCase):
    def setUp(self):
        mommy.make(User, 100)
        self.handler = ModelHandler()
        self.handler.model = User

    def test_slice_single_value(self):
        " single value specified how many items to slice "
        data = User.objects.all()
        
        request = RequestFactory().get('?slice=1')
        sliced, total = self.handler.slice(data, request)
        self.assertItemsEqual(sliced, User.objects.filter(id=1))
        self.assertEqual(total, 100)
    
        data = User.objects.all()
        request = RequestFactory().get('?slice=5')
        sliced, total = self.handler.slice(data, request)
        self.assertItemsEqual(sliced, User.objects.filter(id__lte=5))
        self.assertEqual(total, 100)

    def test_slice_two_values(self):
        " two values, specify starting and stopping elements -1 (zero indexed)"
        data = User.objects.all()
        
        request = RequestFactory().get('?slice=0:2')
        sliced, total = self.handler.slice(data, request)
        self.assertItemsEqual(sliced, User.objects.filter(id__in=[1, 2]))
        self.assertEqual(total, 100)

        data = User.objects.all()
        request = RequestFactory().get('?slice=0:10')
        sliced, total = self.handler.slice(data, request)
        self.assertItemsEqual(sliced, User.objects.filter(id__in=range(1, 11)))
        self.assertEqual(total, 100)

    def test_slice_three_values(self):
        " three values, specify starting, step and stop elements"
        data = User.objects.all()
        
        request = RequestFactory().get('?slice=0:100:20')
        sliced, total = self.handler.slice(data, request)
        self.assertItemsEqual(sliced, User.objects.filter(id__in=[1, 21, 41, 61, 81]))
        self.assertEqual(total, 100)

    def test_more_values(self):
        " more values, should raise an exceptions"
        data = User.objects.all()
        
        request = RequestFactory().get('?slice=0:100:20:10')
        self.assertRaises(
            exceptions.Unprocessable,
            self.handler.slice, 
            data, request
        )            

    def test_invalid_values(self):
        " invalid values, should raise an exception " 
        data = User.objects.all()
        
        request = RequestFactory().get('?slice=0:x')
        self.assertRaises(
            exceptions.Unprocessable,
            self.handler.slice, 
            data, request
        )            
