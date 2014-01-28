"""
This module tests the handler's ``is_method_allowed`` method.
"""

from firestone.handlers import BaseHandler
from firestone.handlers import ModelHandler
from django.test import TestCase
from django.test import RequestFactory
from django.http.response import HttpResponseNotAllowed


def setup_handler(handler, request, *args, **kwargs):
    """
    Mimics the behavior of ``firestone.views.View.__call__``, without of course
    invoking the handler.
    """
    handler.request = request
    handler.args = args
    handler.kwargs = kwargs
    handler.http_methods = ['GET', 'POST']
    return handler

class TestBaseHandlerIsMethodAllowed(TestCase):
    def test_is_method_allowed(self):
        # Create GET request
        request = RequestFactory().get('whateverpath/')
        # Initialize the handler
        handler = setup_handler(BaseHandler(), request, ) 

        # Call handler method ``is_method_allowed``
        self.assertEquals(
            handler.is_method_allowed(request),
            None,
        )

        # Create POST request
        request = RequestFactory().post('whateverpath/')
        # Initialize the handler
        handler = setup_handler(BaseHandler(), request) 
        # Call handler method ``is_method_allowed``
        self.assertEquals(
            handler.is_method_allowed(request),
            None,
        )

        # Create DELETE request
        request = RequestFactory().delete('whateverpath/')
        # Initialize the handler
        handler = setup_handler(BaseHandler(), request) 
        # Call handler method ``is_method_allowed``
        self.assertTrue(isinstance(
            handler.is_method_allowed(request),
            HttpResponseNotAllowed
        ))

        # Create PUT request
        request = RequestFactory().put('whateverpath/')
        # Initialize the handler
        handler = setup_handler(BaseHandler(), request) 
        # Call handler method ``is_method_allowed``
        self.assertTrue(isinstance(
            handler.is_method_allowed(request),
            HttpResponseNotAllowed
        ))
    
class TestModelHandlerIsMethodAllowed(TestCase):        
    def test_is_method_allowed(self):
        # Create GET request
        request = RequestFactory().get('whateverpath/')
        # Initialize the handler
        handler = setup_handler(ModelHandler(), request, ) 
             
        # Call handler method ``is_method_allowed``
        self.assertEquals(
            handler.is_method_allowed(request),
            None,
        )

        # Create POST request
        request = RequestFactory().post('whateverpath/')
        # Initialize the handler
        handler = setup_handler(ModelHandler(), request) 
        # Call handler method ``is_method_allowed``
        self.assertEquals(
            handler.is_method_allowed(request),
            None,
        )

        # Create DELETE request
        request = RequestFactory().delete('whateverpath/')
        # Initialize the handler
        handler = setup_handler(ModelHandler(), request) 
        # Call handler method ``is_method_allowed``
        self.assertTrue(isinstance(
            handler.is_method_allowed(request),
            HttpResponseNotAllowed
        ))

        # Create PUT request
        request = RequestFactory().put('whateverpath/')
        # Initialize the handler
        handler = setup_handler(ModelHandler(), request) 
        # Call handler method ``is_method_allowed``
        self.assertTrue(isinstance(
            handler.is_method_allowed(request),
            HttpResponseNotAllowed
        ))
 

        
        
