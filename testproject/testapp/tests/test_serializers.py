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


class TestSerializeToExcel(TestCase):
    # Of course here we can only check the headers. The content is a binary
    # file
    def test_string(self):
        data = 'somedata'
        
        result, headers = serializers._serialize_to_excel(data) 
        self.assertEquals(
            headers, 
            {'content-type': 'application/vnd.ms-excel', 'content-disposition': 'attachment'}
        )

    def test_list(self):
        data = [1, 2, 3]
        
        result, headers = serializers._serialize_to_excel(data) 
        self.assertEquals(
            headers, 
            {'content-type': 'application/vnd.ms-excel', 'content-disposition': 'attachment'}
        )

    def test_dict(self):
        data = {'key': 'value'}
        
        result, headers = serializers._serialize_to_excel(data) 
        self.assertEquals(
            headers, 
            {'content-type': 'application/vnd.ms-excel', 'content-disposition': 'attachment'}
        )


    def test_datetime(self):
        data = datetime.now()
        
        result, headers = serializers._serialize_to_excel(data) 
        self.assertEquals(
            headers, 
            {'content-type': 'application/vnd.ms-excel', 'content-disposition': 'attachment'}
        )


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

    def test_application_excel(self):     
        self.assertEquals(
            serializers._get_serializer('application/vnd.ms-excel'),
            serializers._serialize_to_excel,
        )

class TestGetSerializationFormat(TestCase):            
    def test_empty_accept_header(self):
        request = RequestFactory().get('/')

        self.assertEquals(
            serializers._get_serialization_format(request),
            'application/json',
        )

    def test_invalid_accept_header(self):
        request = RequestFactory().get(
            '/',
            HTTP_ACCEPT='whatever',
        )
        
        self.assertEquals(
            serializers._get_serialization_format(request),
            'application/json',
        )

    def test_json_accept_header(self):
        request = RequestFactory().get(
            '/',
            HTTP_ACCEPT='application/json',
        )

        self.assertEquals(
            serializers._get_serialization_format(request),
            'application/json',
        )

    def test_excel_accept_header(self):
        request = RequestFactory().get(
            '/',
            HTTP_ACCEPT='application/vnd.ms-excel',
        )

        self.assertEquals(
            serializers._get_serialization_format(request),
            'application/vnd.ms-excel',
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

    def test_excel_ser_format(self):
        data = 'somedata'
        result, headers = serializers.serialize(data, 'application/vnd.ms-excel')
        self.assertEquals(
            headers,
            {'content-type': 'application/vnd.ms-excel', 'content-disposition': 'attachment'}
        )

class TestSerializeResponseData(TestCase):
    def test_serialize_no_accept_header(self):
        request = RequestFactory().get('/')
        data = 'somedata'
        
        result, headers = serializers.serialize_response_data(data, request) 
        self.assertJSONEqual(result, json.dumps(data))
        self.assertEquals(headers, {'content-type': 'application/json'})

    def test_serialize_invalid_accept_header(self):
        # data: list
        request = RequestFactory().get(
            '/',
            HTTP_ACCEPT='whatever'
        )
        data = 'somedata'
        
        result, headers = serializers.serialize_response_data(data, request)
        self.assertJSONEqual(result, json.dumps(data))
        self.assertEquals(headers, {'content-type': 'application/json'})

    def test_serialize_json_accept_header(self):
        request = RequestFactory().get(
            '/',
            HTTP_ACCEPT='application/json',
        )
        data = 'somedata'
        
        result, headers = serializers.serialize_response_data(data, request)
        self.assertJSONEqual(result, json.dumps(data))
        self.assertEquals(headers, {'content-type': 'application/json'})

    def test_serialize_excel_accept_header(self):
        request = RequestFactory().get(
            '/',
            HTTP_ACCEPT='application/vnd.ms-excel',
        )
        data = 'somedata'
        
        result, headers = serializers.serialize_response_data(data, request)
        self.assertEquals(
            headers, 
            {'content-type': 'application/vnd.ms-excel', 'content-disposition': 'attachment'}
        )



