"""
This module tests the ``firestone.deserializers`` module
"""
from firestone.deserializers import _json_deserializer
from firestone.deserializers import _form_encoded_data_deserializer
from firestone.deserializers import _get_deserializer
from firestone.deserializers import deserialize
from firestone.deserializers import deserialize_request_body
from firestone import exceptions
from django.test import TestCase
from django.test import RequestFactory
import urllib


class TestJsonDeserializer(TestCase):
    def test_string(self):
        data = 'string'
        self.assertRaises(ValueError, _json_deserializer, data)

    def test_list(self):
        data = '[1, 2, 3]'
        expected = [1, 2, 3]
        self.assertEqual(_json_deserializer(data), expected)

    def test_json(self):
        data = '{"key": "value"}'
        expected = {'key': 'value'}
        self.assertEqual(_json_deserializer(data), expected)

class TestFormEncodedDataDeserializer(TestCase):
    def test_string(self):
        data = 'string'
        self.assertRaises(ValueError, _form_encoded_data_deserializer, data)

    def test_urlencoded(self):
        data_dic = {'key1': 'value1', 'key2': 'value2'}
        data = urllib.urlencode(data_dic)
        self.assertEqual(_form_encoded_data_deserializer(data), data_dic)

class TestGetDeserializer(TestCase):
    def test_empty(self):
        self.assertIsNone(_get_deserializer(''))

    def test_unsupported(self):        
        self.assertIsNone(_get_deserializer('unsupported media type'))
        
    def test_json(self):        
        self.assertEquals(
            _get_deserializer('application/json'),
            _json_deserializer,
        )

    def test_JSON(self):        
        self.assertEquals(
            _get_deserializer('Application/JSON'),
            _json_deserializer,
        )

    def test_json_utf8(self):        
        self.assertEquals(
            _get_deserializer('application/json; charset=utf-8'),
            _json_deserializer,
        )

    def test_form_encoded(self):        
        self.assertEquals(
            _get_deserializer('application/x-www-form-urlencoded'),
            _form_encoded_data_deserializer,
        )                

    def test_FORM_ENCODED(self):        
        self.assertEquals(
            _get_deserializer('application/X-WWW-FORM-URLENCODED'),
            _form_encoded_data_deserializer,
        )                


class TestDeserialize(TestCase):        
    def test_json_none_content_type(self):
        data = '{"key": "value"}'
        # Empty ``content_type``
        self.assertRaises(
            exceptions.UnsupportedMediaType,
            deserialize,
            data, None
        )
    def test_json_empty_content_type(self):        
        data = '{"key": "value"}'
        self.assertRaises(
            exceptions.UnsupportedMediaType,
            deserialize,
            data, ''
        )
    
    def test_json_unsupported_content_type(self):        
        data = '{"key": "value"}'
        # Unsupported ``content_type``
        self.assertRaises(
            exceptions.UnsupportedMediaType,
            deserialize,
            data, 'unsupported_content_type'
        )

    def test_invalid_data_json_content_type(self):        
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

    def test_invalid_data_form_content_type(self):        
        data = "string"
        self.assertRaises(
            exceptions.BadRequest,
            deserialize,
            data, 'application/x-www-form-urlencoded',
        )

    def test_valid_data_json_content_type(self):            
        # Known content_type, good data
        data = '{"key": "value"}'
        self.assertEquals(
            deserialize(data, 'application/json'),
            {'key': 'value'},
        )

    def test_valid_data_JSON_content_type(self):
        data = '{"key": "value"}'
        self.assertEquals(
            deserialize(data, 'Application/JSON'),
            {'key': 'value'},
        )

    def test_valid_data_json_utf_content_type(self): 
        data = '{"key": "value"}'
        self.assertEquals(
            deserialize(data, 'application/json; charset=utf-8'),
            {'key': 'value'},
        )

    def test_valid_data_form_content_type(self):            
        data_dic = {'key': 'value'}
        data = urllib.urlencode(data_dic)
        self.assertEquals(
            deserialize(data, 'application/x-www-form-urlencoded'),
            data_dic,
        )

    def test_valid_data_FORM_content_type(self):        
        data_dic = {'key': 'value'}
        data = urllib.urlencode(data_dic)
        self.assertEquals(
            deserialize(data, 'application/X-WWW-FORM-URLENCODED'),
            data_dic
        )
        

class TestGetDeserializeRequestBody(TestCase):        
    def test_empty_content_type(self):
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

    def test_unsupported_media_type(self):        
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

    def test_json_content_type_invalid_data_1(self):        
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

    def test_json_content_type_invalid_data_2(self):        
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

    def test_form_content_type_invalid_data(self):
        request = RequestFactory().post(
            '/',
            data='string',
            content_type='application/x-www-form-urlencoded',
        )
        self.assertRaises(
            exceptions.BadRequest,
            deserialize_request_body,
            request,
        )

    def test_json_content_type_valid_data_1(self):        
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

    def test_json_content_type_valid_data_2(self):        
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

    def test_form_content_type_valid_data(self):
        data_dic = {'key1': 'value1', 'key2': 'value2'}

        request = RequestFactory().post(
            '/',
            data=urllib.urlencode(data_dic),
            content_type='application/x-www-form-urlencoded',
        )
        self.assertEqual(
            deserialize_request_body(request),
            data_dic,
        )

    

