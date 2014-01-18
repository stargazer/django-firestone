from django.test import TestCase
from django.test import Client 
import json

class BaseTest(TestCase):
    """
    Very flexible testing class for testing API handlers.

    https://docs.djangoproject.com/en/1.5/topics/testing/overview/
    https://docs.djangoproject.com/en/dev/ref/request-response/
    """
    def setUp(self):
        self.client = Client(HTTP_CONTENT_TYPE='application/json')
        self.method_mapper = {
            'get': self.client.get,
            'post': self.client.post,
            'put': self.client.put,
            'delete': self.client.delete,
        }                

        self.login()

    def login(self):
        self.client.login(
            username=self.USERNAME,
            password=self.PASSWORD,
        )

    def execute(self, request, expected_response):
        """
        @param request: Request specs
        @param response: Expected response specs

        request = {
            'method': 'get',
            'path'  : '/api/handler/,
            'data'  : {},
            'headers': {},
        }
        expected_response = {
            'status_code': 200,
            'content_data_structure': list,
            'content_num': 15,
            'headers': {'content-disposition': 'attachment'},
            ...
            ...
        }
        """
        # TODO: Be able to count num queries
        # TODO: Be able to compare the exact response with the expected
        # response
        
        # Print request details
        print 'Path:%s\tMethod:%s\tData:%s\tHeaders:%s\n' % (
            request.get('path'),
            request.get('method'),
            request.get('data', {}),
            request.get('headers', {}),
        )

        # Execute request and retrieve response
        response = self.method_mapper[
            request['method']](path=request['path'], data=request['data'], **request['headers']
        )
        
        # Extract the response details we need
        response_data = {
            'status_code': response.status_code,
            'headers': {header: response.get(header) for header in expected_response[headers]},
            'content_data_structure': type(response.content),
            'content_num': len(response.content),
        }                

        # Compare to expected
        for param in ('status_code', 'content_data_structure', 'content_num'):
            self.assertEqual(response_data(param), expected_response[param])
        if expected_response.get('headers'):
            for header, value in expected_response['headers'].items():
                self.assertEqual(response_data[header], value)


# Example of an application-level test class.
class HandlerTest(BaseTest):
        USERNAME = 'tester@example.com'
        PASS     = 'pass'

        fixtures = []

        # This is an application level test method            
        def test_method_name(self):         
            # one request
            request = {
                'method': get,
                'path': '/api/handler/'
            }
            response = {
                'status_code': 200,
                'content_data_structure': list,
                'content_num': 14,
                'headers': {'content-disposition': 'attachment'},
                'num_queries': 10,
            }
            self.execute(request, response)

            # another request
            request = {
                'method': 'post',
                'path': '/api/handler/',
                'data': {'key': 'value'},
                'headers': {'content_type': 'application/json'},
            }
            response = {
                'status_code': 200,
                'content_data_structure': dict,
                'content_num': 14,
                'headers': {'content-type': 'application/json'},
                'num_queries':2,
            }
            self.execute(request, response)

