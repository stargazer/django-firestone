"""
This module tests the ``firestone.handlers.BaseHandler.paginate_data`` and
``firestone.handlers.ModelHandler.paginate_data`` methods
"""
from firestone.handlers import BaseHandler
from firestone.handlers import ModelHandler
from firestone import exceptions
from django.test import TestCase
from django.test import RequestFactory
from django.contrib.auth.models import User
from model_mommy import mommy


class BaseHandlerTestPaginateData(TestCase):
    def test_paginate_data(self):
        handler = BaseHandler()
        request = RequestFactory().get('/')
        data = "data"
        page = 1

        self.assertEqual(
            handler.paginate_data(data, page, request),
            (data, {}),
        )


class ModelHandlerTestPaginateData(TestCase):
    def setUp(self):
        self.handler = ModelHandler()
        self.handler.model = User
        self.handler.items_per_page = 10
        self.request = RequestFactory().get('/')
        
        mommy.make(User, 100)

    def test_valid_paging(self):
        data = User.objects.all()
        page = 1
        data_page, pagination = self.handler.paginate_data(data, page, self.request)
        self.assertItemsEqual(data_page, User.objects.filter(id__lte=10))
        self.assertEqual(pagination['total_pages'], 10)
        self.assertEqual(pagination['total_items'], 100)

        page = 10
        data_page, pagination = self.handler.paginate_data(data, page, self.request)
        self.assertItemsEqual(data_page, User.objects.filter(id__in=range(91,101)))
        self.assertEqual(pagination['total_pages'], 10)
        self.assertEqual(pagination['total_items'], 100)

    def test_valid_paging_single_model_instance(self):
        # Data is unpaginable, so returns as is
        data = User.objects.get(id=1)
        page = 1

        self.assertEqual(
            self.handler.paginate_data(data, page, self.request),
            (data, {}),
        )

    def test_invalid_paging(self):
        # Data is unpaginable, so returns as is
        data = User.objects.all()
        page = 1000000
        self.assertEqual(
            self.handler.paginate_data(data, page, self.request),
            (data, {}),
        )
            
        data = User.objects.all()
        page = 'invalid'
        self.assertEqual(
            self.handler.paginate_data(data, page, self.request),
            (data, {}),
        )

        data = User.objects.all()
        page = None
        self.assertEqual(
            self.handler.paginate_data(data, page, self.request),
            (data, {}),
        )

    def test_paging_with_valid_ipp(self):
        data = User.objects.all()
        page = 2
        request = RequestFactory().get('/?ipp=50')
        
        data_page, pagination = self.handler.paginate_data(data, page, request)
        self.assertItemsEqual(data_page, User.objects.filter(id__range=(51, 101)))
        self.assertEqual(pagination['total_pages'], 2)
        self.assertEqual(pagination['total_items'], 100)

    def test_paging_with_invalid_ipp(self):
        # In case of invalid ipp, we fallback to handler.items_per_page
        data = User.objects.all()
        page = 1
        request = RequestFactory().get('/?ipp=invalid')

        data, pagination = self.handler.paginate_data(data, page, request)

        self.assertItemsEqual(data, User.objects.filter(id__in=range(1, 11)))
        self.assertEqual(pagination['total_pages'], 10)
        self.assertEqual(pagination['total_items'], 100)
        
