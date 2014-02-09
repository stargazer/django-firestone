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


class TestCleanModelsSingleModel(TestCase):
    def setUp(self):
       mommy.make(User, 10)

    def test_correct(self):
        handler = ModelHandler()
        handler.model = User

        request = RequestFactory().post('/')
        request.data = User.objects.get(id=1)

        handler.clean_models(request)

    def test_invalid_field_values(self):
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
        else:
            assert(False)

    def test_invalid_general(self):
        """
        We will make the model's clean() method to raise some ValidationError.

        Are errors raised by model.clean() handler correctly?
        They should raise a ``exceptions.BadRequest`` exception.
        """
        old_clean = User.clean
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
        else:
            assert(False)

        User.clean = old_clean            

class TestCleanModelsQueryset(TestCase):
    """
    Errors on some model instance in a queryset, will behave exactly as in the
    case of a single model instance.
    """
    def setUp(self):
        mommy.make(User, 10)

    def test_correct(self):
        handler = ModelHandler()
        handler.model = User

        request = RequestFactory().post('/')
        request.data = User.objects.all()

        handler.clean_models(request)

    def test_invalid_field_values(self):
        """
        We will set some invalid field values.

        Are errors raised by model.clean_fields() handled correctly?
        They should raise a ``exceptions.BadRequest`` exception
        """
        handler = ModelHandler()
        handler.model = User
        
        request = RequestFactory().post('/')
        request.data = User.objects.all()

        # I set some invalid values for some fields of every instance
        for item in request.data:
            item.username = ''
            item.password = ''

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
        else:
            assert(False)
    
    def test_invalid_general(self):
        """
        We will make the model's clean() method to raise some ValidationError.

        Are errors raised by model.clean() handler correctly?
        They should raise a ``exceptions.BadRequest`` exception.
        """
        old_clean = User.clean
        def clean(self):
            raise ValidationError('Error string')
        User.clean = clean

        handler = ModelHandler()
        handler.model = User
        
        request = RequestFactory().post('/')
        request.data = User.objects.all()
        
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
        else:
            assert(False)

        User.clean = old_clean            
