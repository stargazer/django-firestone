"""
This module tests the ``firestone.handlers.BaseHandler.paginate`` module
"""
from firestone.handlers import BaseHandler
from django.test import TestCase
from django.test import RequestFactory


def init_handler(handler, request, *args, **kwargs):
    # Mimicking the initialization of the handler instance
    handler.request = request
    handler.args = args
    handler.kwargs = kwargs
    return handler


class BaseHandlerTestPaginate(TestCase):
    def setUp(self):
        request = RequestFactory().get('/')
        handler = init_handler(BaseHandler(), request)
        self.handler = handler

    def test_no_paging(self):
        handler = self.handler
        data = "data"

        self.assertEqual(
            handler.paginate(data),
            (data, {},)
        )

    def test_paging(self):        
        handler = self.handler
        handler.request = RequestFactory().get('/?page=1')
        data = "data"
        
        self.assertEqual(
            handler.paginate(data),
            (data, {},)
        )
        
    pass


