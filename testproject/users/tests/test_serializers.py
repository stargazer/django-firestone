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


class TestSerializers(TestCase):
    def test_serialize_to_json(self):
        data = 'somedata'

        result, headers = serializers._serialize_to_json(data) 
        self.assertJSONEqual(result, json.dumps(data))
        self.assertEquals(headers, {'content-type': 'application/json'})

        data = [1, 2, 3]
        result, headers = serializers._serialize_to_json(data)
        self.assertJSONEqual(result, json.dumps(data))
        self.assertEquals(headers, {'content-type': 'application/json'})

        data = {'key': 'value'}
        result, headers = serializers._serialize_to_json(data)
        self.assertJSONEqual(result, json.dumps(data))
        self.assertEquals(headers, {'content-type': 'application/json'})

        data = datetime.now()
        result, headers = serializers._serialize_to_json(data)
        self.assertJSONEqual(result, json.dumps(data, cls=DateTimeAwareJSONEncoder))
        self.assertEquals(headers, {'content-type': 'application/json'})

    def test_get_serializer(self):
        self.assertEquals(
            serializers._get_serializer(),
            serializers._serialize_to_json
        )

        self.assertEquals(
            serializers._get_serializer('whatever'),
            serializers._serialize_to_json
        )

        self.assertEquals(
            serializers._get_serializer('application/json'),
            serializers._serialize_to_json
        )

    def test_get_serialization_format(self):
        request = RequestFactory().get('/')

        self.assertEquals(
            serializers._get_serialization_format(request),
            'application/json',
        )

    def test_serialize(self):
        data = 'somedata'
        result, headers = serializers.serialize(data)
        self.assertJSONEqual(result, json.dumps(data))
        self.assertEquals(headers, {'content-type': 'application/json'})

        result, headers = serializers.serialize(data, 'whatever')
        self.assertJSONEqual(result, json.dumps(data))
        self.assertEquals(headers, {'content-type': 'application/json'})

        result, headers = serializers.serialize(data, 'application/json')
        self.assertJSONEqual(result, json.dumps(data))
        self.assertEquals(headers, {'content-type': 'application/json'})

    def test_serialize_request_data(self):
        request = RequestFactory().get('/')
        
        data = 'somedata'
        result, headers = serializers.serialize_request_data(data, request) 
        self.assertJSONEqual(result, json.dumps(data))
        self.assertEquals(headers, {'content-type': 'application/json'})

        data = [1, 2, 3]
        result, headers = serializers.serialize_request_data(data, request)
        self.assertJSONEqual(result, json.dumps(data))
        self.assertEquals(headers, {'content-type': 'application/json'})

        data = {'key': 'value'}
        result, headers = serializers.serialize_request_data(data, request)
        self.assertJSONEqual(result, json.dumps(data))
        self.assertEquals(headers, {'content-type': 'application/json'})

        data = datetime.now()
        result, headers = serializers.serialize_request_data(data, request)
        self.assertJSONEqual(result, json.dumps(data, cls=DateTimeAwareJSONEncoder))
        self.assertEquals(headers, {'content-type': 'application/json'})



