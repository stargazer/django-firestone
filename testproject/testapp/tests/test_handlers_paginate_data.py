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


def init_handler(handler, request, *args, **kwargs):
    # Mimicking the initialization of the handler instance
    handler.request = request
    handler.args = args
    handler.kwargs = kwargs
    return handler


class BaseHandlerTestPaginateData(TestCase):
    def test_paginate_data(self):
        request = RequestFactory().get('/')
        handler = init_handler(BaseHandler(), request)
        data = "data"
        page = 1

        self.assertEqual(
            handler.paginate_data(data, page),
            (data, {}),
        )


class ModelHandlerTestPaginateData(TestCase):
    def setUp(self):
        request = RequestFactory().get('/')
        handler = init_handler(ModelHandler(), request)
        handler.model = User
        handler.items_per_page = 10
        self.handler = handler
        
        mommy.make(User, 100)

    def test_valid_paging_1(self):
        handler = self.handler

        data = User.objects.all()
        page = 1
        data_page, metadata = handler.paginate_data(data, page)
        self.assertItemsEqual(data_page, User.objects.filter(id__lte=10))
        self.assertEqual(metadata['total_pages'], 10)
        self.assertEqual(metadata['total_items'], 100)

    def test_valid_paging_2(self):
        handler = self.handler
        
        data = User.objects.all()
        page = 10
        data_page, metadata = handler.paginate_data(data, page)
        self.assertItemsEqual(data_page, User.objects.filter(id__in=range(91,101)))
        self.assertEqual(metadata['total_pages'], 10)
        self.assertEqual(metadata['total_items'], 100)

    def test_valid_paging_no_metadata(self):
        # handler.pagination_metadata=False
        handler = self.handler
        handler.pagination_metadata = False

        data = User.objects.all()
        page = 1
        data_page, metadata = handler.paginate_data(data, page)
        self.assertItemsEqual(data_page, User.objects.filter(id__lte=10))
        self.assertEqual(metadata, {})

    def test_valid_paging_single_model_instance(self):
        handler = self.handler
        # Data is unpaginable, so returns as is
        data = User.objects.get(id=1)
        page = 1

        self.assertEqual(
            handler.paginate_data(data, page),
            (data, {}),
        )

    def test_invalid_paging_1(self):
        handler = self.handler
        # Data is unpaginable, so returns as is
        data = User.objects.all()
        page = 1000000
        self.assertEqual(
            handler.paginate_data(data, page),
            (data, {}),
        )

    def test_invalid_paging_2(self):
        handler = self.handler

        data = User.objects.all()
        page = 'invalid'
        self.assertEqual(
            handler.paginate_data(data, page),
            (data, {}),
        )

    def test_invalid_paging_3(self):
        handler = self.handler 
        data = User.objects.all()
        page = None
        self.assertEqual(
            handler.paginate_data(data, page),
            (data, {}),
        )

    def test_paging_with_valid_ipp(self):
        handler = self.handler
        data = User.objects.all()
        page = 2
        handler.request = RequestFactory().get('/?ipp=50')
        
        data_page, metadata = self.handler.paginate_data(data, page)
        self.assertItemsEqual(data_page, User.objects.filter(id__range=(51, 101)))
        self.assertEqual(metadata['total_pages'], 2)
        self.assertEqual(metadata['total_items'], 100)

    def test_paging_with_invalid_ipp(self):
        handler = self.handler
        # In case of invalid ipp, we fallback to handler.items_per_page
        data = User.objects.all()
        page = 1
        handler.request = RequestFactory().get('/?ipp=invalid')

        data, metadata = handler.paginate_data(data, page)

        self.assertItemsEqual(data, User.objects.filter(id__in=range(1, 11)))
        self.assertEqual(metadata['total_pages'], 10)
        self.assertEqual(metadata['total_items'], 100)
        
