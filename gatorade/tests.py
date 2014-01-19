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
        self.login()

    def login(self):
        self.client.login(
            username=self.USERNAME,
            password=self.PASSWORD,
        )

    def request(self, request_dict):
        """
        @param request_dict: Dictionary with request specs

        Deserializes the ``request_dict``, translate it to an HTTP request
        on the ``self.client`` client, executres the request, and returns the
        HttpResponse object.
        """
        method_mapper = {
            'GET': self.client.get,
            'POST': self.client.post,
            'PUT': self.client.put,
            'DELETE': self.client.delete,
        }                

        method = request.get('method').upper()
        path = request.get('path')
        data = request.get('data', {})
        headers = request.get('headers', {})

        # Print request details
        print 'Path:%s\tMethod:%s\tData:%s\tHeaders:%s\n' % (
            path,
            method,
            data,
            headers,
        )

        # Execute request and return response object
        return method_mapper[method](path=path, data=data, **headers)

    def response(self, response, expected_response_dict):
        """
        @param response: HTTPResponse object
        @param expected_response_dict: Dictionary with expected response specs

        Takes the ``response`` object and returns a dictionary with its values
        we are interested in
        """
        return {
            'status_code': response.status_code,
            'headers': {header: response.get(header) for header in expected_response_dict['headers']},
            'data': type(response.content),
            'len': len(response.content),
        }

    def execute(self, request_dict, expected_response_dict):
        """
        @param request_dict: Dictionary with request specs
        @param expected_response_dict: Dictionary with expected response specs

        request_dict = {
            'method': 'get',
            'path'  : '/api/handler/,
            'data'  : {},
            'headers': {},
        }
        expected_response_dict = {
            'status_code': 200,
            'data': list,
            'len': 15,
            'headers': {'content-disposition': 'attachment'},
        }
        """
        # TODO: Be able to count num queries
        # TODO: Be able to compare the exact response with the expected
        # response
        
        # Execute request and retrieve response
        response = self.request(request_dict)
        # Extract the response details we need
        actual_response_dict = self.response(response, expected_response_dict)
        
        # Compare to expected
        for param in ('status_code', 'data', 'len'):
            self.assertEqual(actual_response_dict(param), expected_response_dict[param])
        if expected_response.get('headers'):
            for header, value in expected_response_dict['headers'].items():
                self.assertEqual(actual_response_dict[header], value)

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

