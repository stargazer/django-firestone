"""
This module tests the behavior of the metaclass
``firestone.handlers.HandlerMetaClass`` 
"""
from django.test import TestCase
from firestone.handlers import BaseHandler
from firestone.handlers import ModelHandler
from firestone.authentication import SessionAuthentication
from firestone.authentication import NoAuthentication

class BaseHandlerExample(BaseHandler):
    http_methods = ['gEt', 'post', 'DELETE']
    post_body_fields = ('id', 'name', 'surname')
    put_body_fields = ('name', 'surname')
base_handler = BaseHandlerExample()

class ModelHandlerExample(ModelHandler):
    http_methods = ['pOSt', 'Delete']
    authentication = SessionAuthentication
    post_body_fields = ('id', 'name', 'surname')
    put_body_fields = ('name', 'surname')
model_handler = ModelHandlerExample()    


class TestHandlerMetaClass(TestCase):
    def test_base_handler(self):
        # test ``http_methods``
        self.assertItemsEqual(
            base_handler.http_methods, 
            ['GET', 'POST', 'DELETE'],
        )

        # The class we have set the ``authentication`` parameter to, becomes a
        # superclass of the handler class
        self.assertTrue(NoAuthentication in BaseHandlerExample.__bases__)
        # Whereas the ``authentication`` attribute is dissed
        self.assertRaises(
            AttributeError,
            base_handler.authentication,
        )

        # Have these 2 parameters been transformed to sets?
        self.assertIsInstance(base_handler.post_body_fields, set)
        self.assertIsInstance(base_handler.put_body_fields, set)

    def test_model_handler(self):
        self.assertItemsEqual(
            model_handler.http_methods,
            ['POST', 'DELETE'],
        )

        # The class we have set the ``authentication`` parameter to, becomes a
        # superclass of the handler class
        self.assertTrue(SessionAuthentication in ModelHandlerExample.__bases__)
        # Whereas the ``authentication`` attribute is dissed
        self.assertRaises(
            AttributeError,
            model_handler.authentication,
        )
        
        
        # Have these 2 parameters been transformed to sets?
        self.assertIsInstance(model_handler.post_body_fields, set)
        self.assertIsInstance(model_handler.put_body_fields, set)
                

