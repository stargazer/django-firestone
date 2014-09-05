# coding: UTF-8

"""
This module tests the functions in the ``firestone.serializers`` module
"""
from firestone import serializers
from firestone import exceptions
from firestone.handlers import BaseHandler
from firestone.handlers import ModelHandler
from django.test import TestCase
from django.test import RequestFactory
from django.core.serializers.json import DateTimeAwareJSONEncoder
from django.http import HttpResponse
from datetime import datetime
import json


class TestSerializerMixinGetSerializationFormat(TestCase):
    # Method get_serialization_format

    def test_no_accept_header(self):
        request = RequestFactory().get('/')
        s = serializers.SerializerMixin()
        s.request = request

        self.assertEqual(
            s.get_serialization_format(),
            s.DEFAULT_SERIALIZATION_FORMAT,    
        )

    def test_json(self):
        request = RequestFactory().get('/', HTTP_ACCEPT='application/json')
        s = serializers.SerializerMixin()
        s.request = request

        self.assertEqual(
            s.get_serialization_format(),
            'application/json',    
        )

    def test_excel(self):
        request = RequestFactory().get('/', HTTP_ACCEPT='application/vnd.ms-excel')
        s = serializers.SerializerMixin()
        s.request = request

        self.assertEqual(
            s.get_serialization_format(),
            'application/vnd.ms-excel',    
        )


class TestSerializerMixinGetSerializer(TestCase):
    # Method get_serializer

    def test_json(self):
        request = RequestFactory().get('/')
        s = serializers.SerializerMixin()
        s.request = request

        self.assertEqual(
            s.get_serializer('application/json'),
            s.serialize_to_json 
        )

    def test_excel(self):
        request = RequestFactory().get('/')
        s = serializers.SerializerMixin()
        s.request = request
        
        self.assertEqual(
            s.get_serializer('application/vnd.ms-excel'),
            s.serialize_to_excel
        )


class TestSerializerMixinSerializeToJson(TestCase):
    # Method serialize_to_json

    def test_json_string(self):
        request = RequestFactory().get('/')
        s = serializers.SerializerMixin()
        s.request = request

        data = 'some string'
        self.assertEqual(
            s.serialize_to_json(data),
            (json.dumps(data), {'Content-Type': 'application/json; charset=utf-8'})
        )

    def test_json_datetime(self):
        request = RequestFactory().get('/')
        s = serializers.SerializerMixin()
        s.request = request

        data = datetime.now()
        self.assertEqual(
            s.serialize_to_json(data),
            (json.dumps(data, cls=DateTimeAwareJSONEncoder),  {'Content-Type': 'application/json; charset=utf-8'})
        )

    def test_dict(self):
        request = RequestFactory().get('/')
        s = serializers.SerializerMixin()
        s.request = request

        data = {'key': 'value'}
        self.assertEqual(
            s.serialize_to_json(data),
            (json.dumps(data, indent=4), {'Content-Type': 'application/json; charset=utf-8'})
        )

    def test_json_list(self):
        request = RequestFactory().get('/')
        s = serializers.SerializerMixin()
        s.request = request

        data = [1, 2, 3, 'a', 'b']
        self.assertEqual(
            s.serialize_to_json(data),
            (json.dumps(data, indent=4),  {'Content-Type': 'application/json; charset=utf-8'})
        )
        

class TestSerializerMixinSerializeToExcel(TestCase):       
    # Method serialize_to_excel

    def setUp(self):
        request = RequestFactory().get('')
        s = serializers.SerializerMixin()
        s.request = request
        s.template = {'fields': ['name', 'surname']}
        s.excel_filename = 'file.xls'
        self.s = s

    def test_data_incorrect_format_1(self):
        # ``data`` is not in the format {'data': <data>}
        
        data = {'key': 'value'}
        
        self.assertRaises(
            exceptions.Unprocessable,
            self.s.serialize_to_excel,
            data,
        )

    def test_data_incorrect_format_2(self):
        # ``data`` is not in the format {'data': <data>}
         
        data = [1, 2, 3]

        self.assertRaises(
            exceptions.Unprocessable,
            self.s.serialize_to_excel,
            data,
        )

    def test_data_incorrect_format_3(self):        
        # ``data`` is not in the format {'data': <data>}
         
        data = 'string'

        self.assertRaises(
            exceptions.Unprocessable,
            self.s.serialize_to_excel,
            data,
        )

    def test_data_data_incorrect_format(self):        
        # data['data'] is not a dict or list
        data = {'data': 'string'}

        self.assertRaises(
            exceptions.NotAcceptable,
            self.s.serialize_to_excel,
            data,
        )

    def test_dict(self):
        # data['data'] is a dictionary

        data = {'data': {'name': '<name>', 'surname': '<surname>'}}
        
        file, headers = self.s.serialize_to_excel(data)
        self.assertItemsEqual(
            headers,
            {
                'Content-Type': 'application/vnd.ms-excel',
                'Content-Disposition': 'attachment; filename=%s;' % self.s.excel_filename
            }
        )

    def test_list_of_dicts(self):
        # data['data'] is a list of dictionaries
        data = {
            'data': [
                {'name': '<name1>', 'surname': '<surname1>'},
                {'name': '<name2>', 'surname': '<surname2>'},
                {'name': '<name3>', 'surname': '<surname3>'},
        ]}

        
        file, headers = self.s.serialize_to_excel(data)
        self.assertItemsEqual(
            headers,
            {
                'Content-Type': 'application/vnd.ms-excel',
                'Content-Disposition': 'attachment; filename=%s;' % self.s.excel_filename
            }
        )

    def test_list_of_dicts_with_random_keys(self):
        # data['data'] is a list of dicts, whose keys have 
        # nothing to do with ``self.s.template['fields']``

        data = {
            'data': [
                {'key1': '<value1>', 'key2': '<value4>'},
                {'key1': '<value2>', 'key2': '<value5>'},
                {'key1': '<value3>', 'key2': '<value6>'},
        ]}
        
        file, headers = self.s.serialize_to_excel(data)
        self.assertItemsEqual(
            headers,
            {
                'Content-Type': 'application/vnd.ms-excel',
                'Content-Disposition': 'attachment; filename=%s;' % self.s.excel_filename
            }
        )

    def test_nested_dicts(self):
        # data['data'] has values with nested dicts
        data = {
            'data': {
                'name': {'first_name': '<firstname>',
                         'nickname'  : '<nickname>',
                         }         
            }
        }
        
        file, headers = self.s.serialize_to_excel(data)
        self.assertItemsEqual(
            headers,
            {
                'Content-Type': 'application/vnd.ms-excel',
                'Content-Disposition': 'attachment; filename=%s;' % self.s.excel_filename
            }
        )

    def nest_nested_lists(self):        
        # data['data'] has values with nested lists
        data = {
            'data': {
                'name': ['this', 'is', 'a', 'list', {'key': 'value'}],
            }
        }
        
        file, headers = self.s.serialize_to_excel(data)
        self.assertItemsEqual(
            headers,
            {
                'Content-Type': 'application/vnd.ms-excel',
                'Content-Disposition': 'attachment; filename=%s;' % self.s.excel_filename
            }
        )

    def test_unicode_chars(self):
        data = {
            'data': {
                'name': 'Χαράλαμπος',
             }                
        }                

    def test_filename_is_callable(self):
        self.s.excel_filename = lambda: 'file.xls'
        data = {'data': {'name': '<name>', 'surname': '<surname>'}}
        
        file, headers = self.s.serialize_to_excel(data)
        self.assertItemsEqual(
            headers,
            {
                'Content-Type': 'application/vnd.ms-excel',
                'Content-Disposition': 'attachment; filename=%s;' % self.s.excel_filename
            }
        )


class TestSerializerMixinSerialize(TestCase):
    # Method serialize

    def test_serialize(self):
        request = RequestFactory().get('/')
        s = serializers.SerializerMixin()
        s.request = request

        data = [1, 2, 3, 'a', 'b']
        self.assertItemsEqual(
            s.serialize(data),
            (json.dumps(data, indent=4), {'Content-Type':'application/json; charset=utf-8'})
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
            (json.dumps(data, indent=4), {'Content-Type': 'application/json; charset=utf-8'})
        )

class TestSerializerMixinGetResponse(TestCase):
    # Method get_response

    def test_get_response(self):
        request = RequestFactory().get('/')
        s = serializers.SerializerMixin()
        s.request = request

        data = [1, 2, 3, 'a', 'b']
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        self.assertItemsEqual(
            s.get_response(data),
            HttpResponse(json.dumps(data, indent=4), content_type='application/json; charset=utf-8')
        )



    

