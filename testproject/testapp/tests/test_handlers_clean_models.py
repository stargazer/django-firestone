"""
This module tests the ``firestone.handlers.ModelHandler.clean_models`` method.
"""
from firestone.handlers import ModelHandler
from firestone import exceptions
from django.test import TestCase
from django.test import RequestFactory
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from model_mommy import mommy


class TestCleanModels(TestCase):
    def setUp(self):
       mommy.make(User, 10)

    def test_single_model(self):
        handler = ModelHandler()
        handler.model = User

        request = RequestFactory().post('/')
        request.data = User.objects.get(id=1)

        handler.clean_models(request)

    def test_single_model_invalid_field_values(self):
        """
        We will set some invalid field values.

        Are errors raised by model.clean_fields() handled correctly?
        They should raise a ``exceptions.BadRequest`` exception
        """
        handler = ModelHandler()
        handler.model = User
        
        request = RequestFactory().post('/')
        request.data = User.objects.get(id=1)

        # I set some invalid values for some fields
        request.data.username = ''
        request.data.password = ''
        # Does ``clean_models`` raise the correct exception?
        self.assertRaises(
            exceptions.BadRequest,
            handler.clean_models,
            request,
        )

        # Does the exception ``errors`` attribute include a dictionary with the correct keys?
        try:
            handler.clean_models(request)
        except exceptions.BadRequest, e:
            self.assertIsInstance(e.errors, dict)
            self.assertItemsEqual(e.errors.keys(), ('username', 'password'))

    def test_single_model_invalid_general(self):
        """
        We will make the model's clean() method to raise some ValidationError.

        Are errors raised by model.clean() handler correctly?
        They should raise a ``exceptions.BadRequest`` exception.
        """
        def clean(self):
            raise ValidationError('Error string')
        User.clean = clean

        handler = ModelHandler()
        handler.model = User
        
        request = RequestFactory().post('/')
        request.data = User.objects.get(id=1)
        
        # Does ``clean_models`` raise the correct exception?
        self.assertRaises(
            exceptions.BadRequest,
            handler.clean_models,
            request,
        )
        # Does the exception ``errors`` attribute include a dictionary of the
        # correct form?
        try:
            handler.clean_models(request)
        except exceptions.BadRequest, e:
            self.assertIsInstance(e.errors, dict)
            self.assertEqual(e.errors['__all__'][0], 'Error string')

    def test_queryset(self):
        pass

