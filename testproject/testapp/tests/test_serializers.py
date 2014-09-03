"""
This module tests the functions in the ``firestone.serializers`` module
"""
from firestone import serializers
from firestone.handlers import BaseHandler
from firestone.handlers import ModelHandler
from django.test import TestCase
from django.test import RequestFactory
from django.core.serializers.json import DateTimeAwareJSONEncoder
from datetime import datetime
import json


class TestSerializeToJson(TestCase):
    def test_string(self):
        data = 'somedata'

        result, headers = serializers._serialize_to_json(data) 
        self.assertJSONEqual(result, json.dumps(data))
        self.assertEquals(headers, {'content-type': 'application/json'})

    def test_list(self):
        data = [1, 2, 3]
        result, headers = serializers._serialize_to_json(data)
        self.assertJSONEqual(result, json.dumps(data))
        self.assertEquals(headers, {'content-type': 'application/json'})

    def test_dict(self):
        data = {'key': 'value'}
        result, headers = serializers._serialize_to_json(data)
        self.assertJSONEqual(result, json.dumps(data))
        self.assertEquals(headers, {'content-type': 'application/json'})

    def test_datetime(self):
        data = datetime.now()
        result, headers = serializers._serialize_to_json(data)
        self.assertJSONEqual(result, json.dumps(data, cls=DateTimeAwareJSONEncoder))
        self.assertEquals(headers, {'content-type': 'application/json'})


class TestGetSerializer(TestCase):
    def test_empty(self):
        self.assertEquals(
            serializers._get_serializer(),
            serializers._serialize_to_json
        )

    def test_invalid(self):
        self.assertEquals(
            serializers._get_serializer('whatever'),
            serializers._serialize_to_json
        )

    def test_application_json(self):        
        self.assertEquals(
            serializers._get_serializer('application/json'),
            serializers._serialize_to_json
        )

class TestGetSerializationFormat(TestCase):            
    def test_empty_header(self):
        request = RequestFactory().get('/')

        self.assertEquals(
            serializers._get_serialization_format(request),
            'application/json',
        )


class TestSerialize(TestCase):
    def test_empty_ser_format(self):
        data = 'somedata'
        result, headers = serializers.serialize(data)
        self.assertJSONEqual(result, json.dumps(data))
        self.assertEquals(headers, {'content-type': 'application/json'})

    def test_invalid_ser_format(self):
        data = 'somedata'
        result, headers = serializers.serialize(data, 'whatever')
        self.assertJSONEqual(result, json.dumps(data))
        self.assertEquals(headers, {'content-type': 'application/json'})

    def test_json_ser_format(self):
        data = 'somedata'
        result, headers = serializers.serialize(data, 'application/json')
        self.assertJSONEqual(result, json.dumps(data))
        self.assertEquals(headers, {'content-type': 'application/json'})


class TestSerializeResponseData(TestCase):
    def test_serialize_string(self):
        request = RequestFactory().get('/')
        data = 'somedata'
        
        result, headers = serializers.serialize_response_data(data, request) 
        self.assertJSONEqual(result, json.dumps(data))
        self.assertEquals(headers, {'content-type': 'application/json'})

    def test_serialize_list(self):
        request = RequestFactory().get('/')
        data = [1, 2, 3]
        
        result, headers = serializers.serialize_response_data(data, request)
        self.assertJSONEqual(result, json.dumps(data))
        self.assertEquals(headers, {'content-type': 'application/json'})

    def test_serialize_dict(self):
        request = RequestFactory().get('/')
        data = {'key': 'value'}
        
        result, headers = serializers.serialize_response_data(data, request)
        self.assertJSONEqual(result, json.dumps(data))
        self.assertEquals(headers, {'content-type': 'application/json'})

    def test_serialize_datetime(self):
        request = RequestFactory().get('/')
        data = datetime.now()
        
        result, headers = serializers.serialize_response_data(data, request)
        self.assertJSONEqual(result, json.dumps(data, cls=DateTimeAwareJSONEncoder))
        self.assertEquals(headers, {'content-type': 'application/json'})



