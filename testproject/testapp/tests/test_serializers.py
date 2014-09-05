"""
This module tests the functions in the ``firestone.serializers`` module
"""
from firestone import serializers
from firestone.handlers import BaseHandler
from firestone.handlers import ModelHandler
from django.test import TestCase
from django.test import RequestFactory
from django.core.serializers.json import DateTimeAwareJSONEncoder
from django.http import HttpResponse
from datetime import datetime
import json


class TestSerializerMixin(TestCase):
    def test_get_serialization_format_no_accept_header(self):
        request = RequestFactory().get('/')
        s = serializers.SerializerMixin()
        s.request = request

        self.assertEqual(
            s.get_serialization_format(),
            s.DEFAULT_SERIALIZATION_FORMAT,    
        )

    def test_get_serialization_format_json(self):
        request = RequestFactory().get('/', HTTP_ACCEPT='application/json')
        s = serializers.SerializerMixin()
        s.request = request

        self.assertEqual(
            s.get_serialization_format(),
            'application/json',    
        )

    def test_get_serialization_format_excel(self):
        request = RequestFactory().get('/', HTTP_ACCEPT='application/vnd.ms-excel')
        s = serializers.SerializerMixin()
        s.request = request

        self.assertEqual(
            s.get_serialization_format(),
            'application/vnd.ms-excel',    
        )

    def test_get_serializer_json(self):
        request = RequestFactory().get('/')
        s = serializers.SerializerMixin()
        s.request = request

        self.assertEqual(
            s.get_serializer('application/json'),
            s.serialize_to_json 
        )

    def test_get_serializer_excel(self):
        request = RequestFactory().get('/')
        s = serializers.SerializerMixin()
        s.request = request
        
        self.assertEqual(
            s.get_serializer('application/vnd.ms-excel'),
            s.serialize_to_excel
        )

    def test_serialize_to_json_string(self):
        request = RequestFactory().get('/')
        s = serializers.SerializerMixin()
        s.request = request

        data = 'some string'
        self.assertEqual(
            s.serialize_to_json(data),
            (json.dumps(data), {'Content-Type': 'application/json'})
        )

    def test_serializer_to_json_datetime(self):
        request = RequestFactory().get('/')
        s = serializers.SerializerMixin()
        s.request = request

        data = datetime.now()
        self.assertEqual(
            s.serialize_to_json(data),
            (json.dumps(data, cls=DateTimeAwareJSONEncoder),  {'Content-Type': 'application/json'})
        )

    def test_serializer_to_json_dict(self):
        request = RequestFactory().get('/')
        s = serializers.SerializerMixin()
        s.request = request

        data = {'key': 'value'}
        self.assertEqual(
            s.serialize_to_json(data),
            (json.dumps(data, indent=4), {'Content-Type': 'application/json'})
        )

    def test_serializer_to_json_list(self):
        request = RequestFactory().get('/')
        s = serializers.SerializerMixin()
        s.request = request

        data = [1, 2, 3, 'a', 'b']
        self.assertEqual(
            s.serialize_to_json(data),
            (json.dumps(data, indent=4),  {'Content-Type': 'application/json'})
        )
        
    def test_serialize_to_excel(self):
        pass

    def test_get_response(self):
        request = RequestFactory().get('/')
        s = serializers.SerializerMixin()
        s.request = request

        data = [1, 2, 3, 'a', 'b']
        headers = {'Content-Type': 'application/json'}
        self.assertItemsEqual(
            s.get_response(data),
            HttpResponse(json.dumps(data, indent=4), content_type='application/json')
        )

    def test_serialize(self):
        request = RequestFactory().get('/')
        s = serializers.SerializerMixin()
        s.request = request

        data = [1, 2, 3, 'a', 'b']
        self.assertItemsEqual(
            s.serialize(data),
            (json.dumps(data, indent=4), {'Content-Type':'application/json'})
        )
        
    def test_serialize_with_ser_format(self):
        #accept header requests excel
        request = RequestFactory().get('/', HTTP_ACCEPT='application/vnd.ms-excel')

        s = serializers.SerializerMixin()
        s.request = request

        # But ``serialize`` is called with ``application/json``
        data = [1, 2, 3, 'a', 'b']
        self.assertItemsEqual(
            s.serialize(data, 'application/json'),
            (json.dumps(data, indent=4), {'Content-Type': 'application/json'})
        )


    

