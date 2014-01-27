"""
This module tests the handler's ``is_method_allowed`` method.
"""

from firestone.handlers import BaseHandler
from firestone.handlers import ModelHandler
from django.test import TestCase
from django.test import RequestFactory
from django.http.response import HttpResponseNotAllowed


def setup_view(view, request, *args, **kwargs):
    """
    Mimics the behavior of django.views.generics.base.View.as_view()
    """
    view.http_method_names = ['get', 'post']
    view.request = request
    view.args = args
    view.kwargs = kwargs
    return view

class TestBaseHandlerIsMethodAllowed(TestCase):
    def test_is_method_allowed(self):
        # Create GET request
        request = RequestFactory().get('whateverpath/')
        # Initialize the handler
        handler = setup_view(BaseHandler(), request, ) 

        # Call handler method ``is_method_allowed``
        self.assertEquals(
            handler.is_method_allowed(request),
            None,
        )

        # Create POST request
        request = RequestFactory().post('whateverpath/')
        # Initialize the handler
        handler = setup_view(BaseHandler(), request) 
        # Call handler method ``is_method_allowed``
        self.assertEquals(
            handler.is_method_allowed(request),
            None,
        )

        # Create DELETE request
        request = RequestFactory().delete('whateverpath/')
        # Initialize the handler
        handler = setup_view(BaseHandler(), request) 
        # Call handler method ``is_method_allowed``
        self.assertTrue(isinstance(
            handler.is_method_allowed(request),
            HttpResponseNotAllowed
        ))

        # Create PUT request
        request = RequestFactory().put('whateverpath/')
        # Initialize the handler
        handler = setup_view(BaseHandler(), request) 
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
        handler = setup_view(ModelHandler(), request, ) 
             
        # Create GET request
        request = RequestFactory().get('whateverpath/')
        # Initialize the handler
        handler = setup_view(ModelHandler(), request, ) 

        # Call handler method ``is_method_allowed``
        self.assertEquals(
            handler.is_method_allowed(request),
            None,
        )

        # Create POST request
        request = RequestFactory().post('whateverpath/')
        # Initialize the handler
        handler = setup_view(ModelHandler(), request) 
        # Call handler method ``is_method_allowed``
        self.assertEquals(
            handler.is_method_allowed(request),
            None,
        )

        # Create DELETE request
        request = RequestFactory().delete('whateverpath/')
        # Initialize the handler
        handler = setup_view(ModelHandler(), request) 
        # Call handler method ``is_method_allowed``
        self.assertTrue(isinstance(
            handler.is_method_allowed(request),
            HttpResponseNotAllowed
        ))

        # Create PUT request
        request = RequestFactory().put('whateverpath/')
        # Initialize the handler
        handler = setup_view(ModelHandler(), request) 
        # Call handler method ``is_method_allowed``
        self.assertTrue(isinstance(
            handler.is_method_allowed(request),
            HttpResponseNotAllowed
        ))
 

        
        
