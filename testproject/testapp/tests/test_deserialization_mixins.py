"""
Testing the ``deserialization_mixins`` module
"""
from firestone.deserialization_mixins import _json_deserializer,\
                                             _form_encoded_data_deserializer,\
                                             _get_deserializer                                             
from django.test import TestCase
from django.utils.http import urlencode


class TestJSONDeserialier(TestCase):
    """
    Tests the ``_json_deserializer`` function
    """
    def test_string(self):
        data = 'string'
        self.assertRaises(ValueError, _json_deserializer, data)

    def test_jsonlist(self):
        data = '[1, 2, 3]'
        expected = [1, 2, 3]
        self.assertEqual(_json_deserializer(data), expected)

    def test_jsondict(self):
        data = '{"key": "value"}'
        expected = {'key': 'value'}
        self.assertEqual(_json_deserializer(data), expected)


class TestFormEncodedDataDeserializer(TestCase):
    """
    Tests the ``_form_encoded_data_deserializer`` function
    """
    def test_string(self):
        data = 'string'
        self.assertRaises(ValueError, _form_encoded_data_deserializer, data)

    def test_urlencoded_dict(self):
        data_dic = {'key1': 'value1', 'key2': 'value2'}
        data = urlencode(data_dic)
        self.assertEqual(_form_encoded_data_deserializer(data), data_dic)

class TestGetDeserializer(TestCase):
    """
    Tests the ``_get_deserializer`` function
    """
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



