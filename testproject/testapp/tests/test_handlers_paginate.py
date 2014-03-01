"""
This module tests the ``firestone.handlers.BaseHandler.paginate`` module
"""
from firestone.handlers import BaseHandler
from django.test import TestCase
from django.test import RequestFactory


class BaseHandlerTestPaginate(TestCase):
    def test_no_paging(self):
        handler = BaseHandler()
        request = RequestFactory().get('/')
        data = "data"

        self.assertEqual(
            handler.paginate(data, request),
            (data, {},)
        )

    def test_paging(self):
        handler = BaseHandler()
        request = RequestFactory().get('/?page=1')
        data = "data"
        
        self.assertEqual(
            handler.paginate(data, request),
            (data, {},)
        )
        
    pass


