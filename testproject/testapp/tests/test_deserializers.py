"""
This module tests the ``firestone.deserializers`` module
"""
from django.test import TestCase
from django.test import RequestFactory
from firestone.deserializers import _json_deserializer
from firestone.deserializers import _get_deserializer
from firestone.deserializers import deserialize
from firestone.deserializers import deserialize_request_body
from firestone import exceptions


class TestDeserializers(TestCase):
    def test_json_deserializer(self):
        data = 'string'
        self.assertRaises(ValueError, _json_deserializer, data)

        data = '[1, 2, 3]'
        expected = [1, 2, 3]
        self.assertEqual(_json_deserializer(data), expected)

        data = '{"key": "value"}'
        expected = {'key': 'value'}
        self.assertEqual(_json_deserializer(data), expected)


    def test_get_deserializer(self):
        self.assertIsNone(_get_deserializer(''))

        self.assertIsNone(_get_deserializer('unsupported media type'))
        
        self.assertEquals(
            _get_deserializer('application/json'),
            _json_deserializer,
        )

        self.assertEquals(
            _get_deserializer('Application/JSON'),
            _json_deserializer,
        )

        self.assertEquals(
            _get_deserializer('application/json; charset=utf-8'),
            _json_deserializer,
        )

    def test_deserialize(self):
        data = '{"key": "value"}'
        # Empty ``content_type``
        self.assertRaises(
            exceptions.UnsupportedMediaType,
            deserialize,
            data, None
        )
        self.assertRaises(
            exceptions.UnsupportedMediaType,
            deserialize,
            data, ''
        )

        # Unsupported ``content_type``
        self.assertRaises(
            exceptions.UnsupportedMediaType,
            deserialize,
            data, 'unsupported_content_type'
        )

        # Known content_type, bad data
        data = "string"
        self.assertRaises(
            exceptions.BadRequest,
            deserialize,
            data, 'application/json',
        )
        data = "{key: value}"
        self.assertRaises(
            exceptions.BadRequest,
            deserialize,
            data, 'application/json',
        )


        # Known content_type, good data
        data = '{"key": "value"}'
        self.assertEquals(
            deserialize(data, 'application/json'),
            {'key': 'value'},
        )
        self.assertEquals(
            deserialize(data, 'Application/JSON'),
            {'key': 'value'},
        )
        self.assertEquals(
            deserialize(data, 'application/json; charset=utf-8'),
            {'key': 'value'},
        )
        
        # Known content_type, good data
        data = "[1, 2, 3]"
        self.assertEquals(
            deserialize(data, 'application/json'),
            [1, 2, 3],
        )
        self.assertEquals(
            deserialize(data, 'Application/JSON'),
            [1, 2, 3],
        )
        self.assertEquals(
            deserialize(data, 'application/json; charset=utf-8'),
            [1, 2, 3],
        )


    def test_get_deserialize_request_body_post(self):
        """ POST requests"""
        # Empty ``Content-type`` header
        request = RequestFactory().post(
            '/', 
            data='{"key": "value"}',
            content_type='',
        )
        self.assertRaises(
            exceptions.UnsupportedMediaType,
            deserialize_request_body,
            request,
        )
        
        # Unsupported media type
        request = RequestFactory().post(
            '/', 
            data='{"key": "value"}',
            content_type='unsupported media type',
        )
        self.assertRaises(
            exceptions.UnsupportedMediaType,
            deserialize_request_body,
            request,
        )

        # Known Content-Type, bad data
        request = RequestFactory().post(
            '/', 
            data='string',
            content_type='application/json',
        )
        self.assertRaises(
            exceptions.BadRequest,
            deserialize_request_body,
            request,
        )

        # Known Content-Type, bad data
        request = RequestFactory().post(
            '/', 
            data='{lala}',
            content_type='application/json',
        )
        self.assertRaises(
            exceptions.BadRequest,
            deserialize_request_body,
            request,
        )

        # Known Content-Type, good data
        request = RequestFactory().post(
            '/', 
            data='[1, 2, 3]',
            content_type='application/json',
        )
        self.assertEqual(
            deserialize_request_body(request),
            [1, 2, 3],
        )

        # Known Content-Type, good data
        request = RequestFactory().post(
            '/', 
            data='{"key": "value"}',
            content_type='application/json',
        )
        self.assertEqual(
            deserialize_request_body(request),
            {'key': 'value'},
        )

    
    def test_get_deserialize_request_body_put(self):
        """ PUT requests"""

        # Empty ``Content-type`` header
        request = RequestFactory().put(
            '/', 
            data='{"key": "value"}',
            content_type='',
        )
        self.assertRaises(
            exceptions.UnsupportedMediaType,
            deserialize_request_body,
            request,
        )
        
        # Unsupported media type
        request = RequestFactory().put(
            '/', 
            data='{"key": "value"}',
            content_type='unsupported media type',
        )
        self.assertRaises(
            exceptions.UnsupportedMediaType,
            deserialize_request_body,
            request,
        )

        # Known Content-Type, bad data
        request = RequestFactory().put(
            '/', 
            data='string',
            content_type='application/json',
        )
        self.assertRaises(
            exceptions.BadRequest,
            deserialize_request_body,
            request,
        )

        # Known Content-Type, bad data
        request = RequestFactory().put(
            '/', 
            data='{lala}',
            content_type='application/json',
        )
        self.assertRaises(
            exceptions.BadRequest,
            deserialize_request_body,
            request,
        )

        # Known Content-Type, good data
        request = RequestFactory().put(
            '/', 
            data='[1, 2, 3]',
            content_type='application/json',
        )
        self.assertEqual(
            deserialize_request_body(request),
            [1, 2, 3],
        )

        # Known Content-Type, good data
        request = RequestFactory().put(
            '/', 
            data='{"key": "value"}',
            content_type='application/json',
        )
        self.assertEqual(
            deserialize_request_body(request),
            {'key': 'value'},
        )

 
