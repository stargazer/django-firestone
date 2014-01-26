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

class IsMethodAllowed(TestCase):
    def test_basehandler(self):
        """
        Testing a base handler's ``http_method_names`` parameter bahavior.
        """
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
    
    def test_modelhandler(self):
        """
        Testing a model handler's ``http_method_names`` parameter bahavior.
        """
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
 

        
        
