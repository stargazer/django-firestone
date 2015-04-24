"""
Testing the ``deserialization_mixins`` module
"""
from firestone.deserialization_mixins import _json_deserializer,\
                                             _form_urlencoded_data_deserializer,\
                                             _get_deserializer,\
                                             DeserializationMixin
                                             
from django.test import TestCase, RequestFactory
from django.utils.http import urlencode
import json


class TestJSONDeserializer(TestCase):
    """
    Tests the ``_json_deserializer`` function
    """
    def test_string(self):
        data = 'string'
        self.assertRaises(
            ValueError, 
            _json_deserializer, 
            data
        )

    def test_jsonlist(self):
        data = '[1, 2, 3]'
        deserialized_data = [1, 2, 3]
        self.assertEqual(
            _json_deserializer(data),
            deserialized_data
        )

    def test_jsondict(self):
        dic = {
            'keyA': 'valueA',
            'keyB': ['valueA', 'valueB'],
            'keyC': 1,
            'keyD': [1, 2],
        }

        data = json.dumps(dic)
        deserialized_data = dic

        self.assertEqual(
            _json_deserializer(data), 
            deserialized_data
        )

class TestFormEncodedDataDeserializer(TestCase):
    """
    Tests the ``_form_urlencoded_data_deserializer`` function
    """
    def test_string(self):
        data = 'string'
        self.assertRaises(
            ValueError, 
            _form_urlencoded_data_deserializer, 
            data
        )

    def test_urlencoded(self):
        dic = {
            'keyA': 'valueA',
            'keyB': ['valueA', 'valueB'],
            'keyC': 1,
            'keyD': [1, 2],
        }

        # URL encode the ``dic``
        data = urlencode(dic, doseq=True)
        # Expected deserialized data: 
        # After deserializing a url encoded data structure, all its values are
        # considered to be strings
        deserialized_data = {
            'keyA': 'valueA',
            'keyB': ['valueA', 'valueB'],
            'keyC': '1',
            'keyD': ['1', '2'],
        }        

        self.assertEqual(
            _form_urlencoded_data_deserializer(data),
            deserialized_data
        )


class TestGetDeserializer(TestCase):
    """
    Tests the ``_get_deserializer`` function
    """
    def test_empty(self):
        self.assertRaises(
            TypeError,
            _get_deserializer,
            '',
        )

    def test_unsupported(self):        
        self.assertRaises(
            TypeError,
            _get_deserializer,
            'unsupported media type',
        )
        
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

    def test_form_urlencoded(self):        
        self.assertEquals(
            _get_deserializer('application/x-www-form-urlencoded'),
            _form_urlencoded_data_deserializer,
        )                

    def test_FORM_URLENCODED(self):        
        self.assertEquals(
            _get_deserializer('application/X-WWW-FORM-URLENCODED'),
            _form_urlencoded_data_deserializer,
        )                


class TestDeserializationMixin(TestCase):
    """
    Tests the ``DeserializationMixin.deserialize`` method
    """
    def setUp(self):
        self.dm = DeserializationMixin()

    def test_valid_content_type_json(self):
        dic = {
            'keyA': 'valueA',
            'keyB': ['valueA', 'valueB'],
            'keyC': 1,
            'keyD': [1, 2],
        }

        payload = json.dumps(dic)
        expected_deserialized_data = dic
        
        request = RequestFactory().post(
            '', 
            data=payload,
            content_type='application/json',
        )
        self.dm.request = request
        
        self.assertEqual(
            self.dm.deserialize(),
            expected_deserialized_data,
        )

        def test_valid_content_type_form_urlencoded(self):
            dic = {
                'keyA': 'valueA',
                'keyB': ['valueA', 'valueB'],
                'keyC': 1,
                'keyD': [1, 2],
            }

            payload = urlencode(dic, doseq=True)
            expected_deserialized_data = {
                'keyA': 'valueA',
                'keyB': ['valueA', 'valueB'],
                'keyC': '1',
                'keyD': ['1', '2'],
            }

            request = RequestFactory().post(
                '', 
                data=payload,
                content_type='application/x-www-form-urlencoded',
            )
            self.dm.request = request
            
            self.assertEqual(
                self.dm.deserialize(),
                expected_deserialized_data,
            )

        def test_no_content_type(self):
            payload = 'whatever'
            request = RequestFactory().post(
                '',
                data=payload,
                content_type='',
            )
            self.dm.request = request

            self.assertRaises(
                TypeError,
                self.dm.deserialize,
            )

        def test_unknown_content_type(self):
            payload = 'whatever'
            request = RequestFactory().post(
                '',
                data=payload,
                content_type='unknown',
            )
            self.dm.request = request

            self.assertRaises(
                ValueError,
                self.dm.deserialize,
            )
