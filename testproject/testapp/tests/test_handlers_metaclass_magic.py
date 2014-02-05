"""
This module tests the behavior of the metaclass
``firestone.handlers.HandlerMetaClass`` 
"""
from django.test import TestCase
from firestone.handlers import BaseHandler
from firestone.handlers import ModelHandler
from firestone.authentication import DjangoAuthentication
from firestone.authentication import NoAuthentication

class BaseHandlerExample(BaseHandler):
    http_methods = ['gEt', 'post', 'DELETE']
    post_body_fields = ('id', 'name', 'surname')
    put_body_fields = ('name', 'surname')
base_handler = BaseHandlerExample()

class ModelHandlerExample(ModelHandler):
    http_methods = ['pOSt', 'Delete']
    authentication = DjangoAuthentication
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

        # test``authentication``
        self.assertTrue(isinstance(base_handler.authentication, NoAuthentication))

        # Have these 2 parameters been transformed to sets?
        self.assertIsInstance(base_handler.post_body_fields, set)
        self.assertIsInstance(base_handler.put_body_fields, set)

    def test_model_handler(self):
        self.assertItemsEqual(
            model_handler.http_methods,
            ['POST', 'DELETE'],
        )

        # test``authentication``
        self.assertTrue(isinstance(model_handler.authentication, DjangoAuthentication))

        # Have these 2 parameters been transformed to sets?
        self.assertIsInstance(model_handler.post_body_fields, set)
        self.assertIsInstance(model_handler.put_body_fields, set)
                

