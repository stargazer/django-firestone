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
            'GET': self.client.get,
            'POST': self.client.post,
            'PUT': self.client.put,
            'DELETE': self.client.delete,
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
            'data': list,
            'len': 15,
            'headers': {'content-disposition': 'attachment'},
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
            request['method'.upper()]](path=request['path'], data=request['data'], **request['headers']
        )
        
        # Extract the response details we need
        response_data = {
            'status_code': response.status_code,
            'headers': {header: response.get(header) for header in expected_response[headers]},
            'data': type(response.content),
            'len': len(response.content),
        }                

        # Compare to expected
        for param in ('status_code', 'data', 'len'):
            self.assertEqual(response_data(param), expected_response[param])
        if expected_response.get('headers'):
            for header, value in expected_response['headers'].items():
                self.assertEqual(response_data[header], value)


# Example of an application-level test class.
class HandlerTest(BaseTest):
        USERNAME = 'tester@example.com'
        PASS     = 'pass'

        fixtures = []

        def test_method_name(self):         
            # one request
            request = dict(method='get', path='/api/handler/')
            response = dict(
                status_code=200, data=list, len= 14,
                headers={'content-disposition': 'attachment'},
                num_queries=10,
            )
            self.execute(request, response)

            # another request
            request = {
                'data': {'key': 'value'},
                'method': 'post', 'path': '/api/handler/',
                'data': {'key': 'value'},
                'headers': {'content_type': 'application/json'},
            }
            response = {
                'status_code': 200, 'data': dict, 'len': 14,
                'headers': {'content-type': 'application/json'},
                'num_queries':2,
            }
            self.execute(request, response)

