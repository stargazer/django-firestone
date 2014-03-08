"""
This module tests the ``firestone.handlers.ModelHandler.clean_models`` method.
"""
from firestone.handlers import ModelHandler
from firestone import exceptions
from django.test import TestCase
from django.test import RequestFactory
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.exceptions import NON_FIELD_ERRORS
from model_mommy import mommy


def init_handler(handler, request, *args, **kwargs):
    # Mimicking the initialization of the handler instance
    handler.request = request
    handler.args = args
    handler.kwargs = kwargs
    return handler


class TestCleanModelsSingleModel(TestCase):
    def setUp(self):
        request = RequestFactory().post('/')
        handler = init_handler(ModelHandler(), request)
        handler.model = User
        self.handler = handler

        mommy.make(User, 10)

    def test_correct(self):
        handler = self.handler
        handler.request.data = User.objects.get(id=1)

        handler.clean_models()

    def test_invalid_field_values(self):
        """
        We will set some invalid field values.

        Are errors raised by model.clean_fields() handled correctly?
        They should raise a ``exceptions.BadRequest`` exception
        """
        handler = self.handler
        handler.request.data = User.objects.get(id=1)

        # I set some invalid values for some fields
        handler.request.data.username = ''
        handler.request.data.password = ''
        # Does ``clean_models`` raise the correct exception?
        self.assertRaises(
            exceptions.BadRequest,
            handler.clean_models,
        )

        # Does the exception ``errors`` attribute include a dictionary with the correct keys?
        try:
            handler.clean_models()
        except exceptions.BadRequest, e:
            self.assertIsInstance(e.errors, dict)
            self.assertItemsEqual(e.errors.keys(), ('username', 'password'))
        else:
            assert(False)

    def test_invalid_general(self):
        """
        We will make the model's clean() method to raise some ValidationError.

        Are errors raised by model.clean() handler correctly?
        They should raise a ``exceptions.BadRequest`` exception.
        """
        old_clean = User.clean
        def new_clean(self):
            raise ValidationError('Error string')
        User.clean = new_clean

        handler = self.handler
        handler.request.data = User.objects.get(id=1)
        
        # Does ``clean_models`` raise the correct exception?
        self.assertRaises(
            exceptions.BadRequest,
            handler.clean_models,
        )
        # Does the exception ``errors`` attribute include a dictionary of the
        # correct form?
        try:
            handler.clean_models()
        except exceptions.BadRequest, e:
            self.assertIsInstance(e.errors, dict)
            self.assertEqual(e.errors[NON_FIELD_ERRORS][0], 'Error string')
        else:
            assert(False)

        User.clean = old_clean            

class TestCleanModelsQueryset(TestCase):
    """
    Errors on some model instance in a queryset, will behave exactly as in the
    case of a single model instance.
    """
    def setUp(self):
        request = RequestFactory().post('/')
        handler = init_handler(ModelHandler(), request)
        handler.model = User
        self.handler = handler

        mommy.make(User, 10)

    def test_correct(self):
        handler = self.handler
        handler.request.data = User.objects.all()

        handler.clean_models()
        assert(True)

    def test_invalid_field_values(self):
        """
        We will set some invalid field values.

        Are errors raised by model.clean_fields() handled correctly?
        They should raise a ``exceptions.BadRequest`` exception
        """
        handler = self.handler
        handler.request.data = User.objects.all()

        # I set some invalid values for some fields of every instance
        for item in handler.request.data:
            item.username = ''
            item.password = ''

        # Does ``clean_models`` raise the correct exception?
        self.assertRaises(
            exceptions.BadRequest,
            handler.clean_models,
        )

        # Does the exception ``errors`` attribute include a dictionary with the correct keys?
        try:
            handler.clean_models()
        except exceptions.BadRequest, e:
            self.assertIsInstance(e.errors, dict)
            self.assertItemsEqual(e.errors.keys(), ('username', 'password'))
        else:
            assert(False)
    
    def test_invalid_general(self):
        """
        We will make the model's clean() method to raise some ValidationError.

        Are errors raised by model.clean() handler correctly?
        They should raise a ``exceptions.BadRequest`` exception.
        """
        old_clean = User.clean
        def new_clean(self):
            raise ValidationError('Error string')
        User.clean = new_clean

        handler = self.handler
        handler.request.data = User.objects.all()
        
        # Does ``clean_models`` raise the correct exception?
        self.assertRaises(
            exceptions.BadRequest,
            handler.clean_models,
        )
        # Does the exception ``errors`` attribute include a dictionary of the
        # correct form?
        try:
            handler.clean_models()
        except exceptions.BadRequest, e:
            self.assertIsInstance(e.errors, dict)
            self.assertEqual(e.errors[NON_FIELD_ERRORS][0], 'Error string')
        else:
            assert(False)

        User.clean = old_clean            
