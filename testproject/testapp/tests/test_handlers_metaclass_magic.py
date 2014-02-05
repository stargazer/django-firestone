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
base_handler = BaseHandlerExample()

class ModelHandlerExample(ModelHandler):
    http_methods = ['pOSt', 'Delete']
    authentication = DjangoAuthentication
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

    def test_model_handler(self):
        self.assertItemsEqual(
            model_handler.http_methods,
            ['POST', 'DELETE'],
        )

        # test``authentication``
        self.assertTrue(isinstance(model_handler.authentication, DjangoAuthentication))


                

