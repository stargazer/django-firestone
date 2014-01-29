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
        self.assertEquals(headers, {'content_type': 'application/json'})

        data = [1, 2, 3]
        result, headers = serializers._serialize_to_json(data)
        self.assertJSONEqual(result, json.dumps(data))
        self.assertEquals(headers, {'content_type': 'application/json'})

        data = {'key': 'value'}
        result, headers = serializers._serialize_to_json(data)
        self.assertJSONEqual(result, json.dumps(data))
        self.assertEquals(headers, {'content_type': 'application/json'})

        data = datetime.now()
        result, headers = serializers._serialize_to_json(data)
        self.assertJSONEqual(result, json.dumps(data, cls=DateTimeAwareJSONEncoder))
        self.assertEquals(headers, {'content_type': 'application/json'})

    def test_get_serializer(self):
        request = RequestFactory().get('/')
                
        self.assertEquals(
            serializers._get_serializer(request),
            serializers._serialize_to_json
        )

    def test_serialize(self):
        request = RequestFactory().get('/')
        
        data = 'somedata'
        result, headers = serializers.serialize(data, request) 
        self.assertJSONEqual(result, json.dumps(data))
        self.assertEquals(headers, {'content_type': 'application/json'})

        data = [1, 2, 3]
        result, headers = serializers.serialize(data, request)
        self.assertJSONEqual(result, json.dumps(data))
        self.assertEquals(headers, {'content_type': 'application/json'})

        data = {'key': 'value'}
        result, headers = serializers.serialize(data, request)
        self.assertJSONEqual(result, json.dumps(data))
        self.assertEquals(headers, {'content_type': 'application/json'})

        data = datetime.now()
        result, headers = serializers.serialize(data, request)
        self.assertJSONEqual(result, json.dumps(data, cls=DateTimeAwareJSONEncoder))
        self.assertEquals(headers, {'content_type': 'application/json'})



