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

    def login(self):
        # TODO: Based on API handler's authentication type, we should be able to
        # login using other methods as well.
        # eg, sign request
        self.client.login(
            username=self.USERNAME,
            password=self.PASSWORD,
        )

    def execute(self, request_dict, expected_response_dict):
        """
        @param request_dict: Dictionary with request specs
        @param expected_response_dict: Dictionary with expected response specs

        This is the only method that the application-level test needs to know
        and invoke.

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
        # TODO: Maybe ``self.login`` should be invoked here. This way it will:
        # - have the same effect
        # - fascilitate the use of other auth mechanisms that require access to
        # request data, in order to add header or querystring parameter in the request.
        self.login()

        # Execute request and retrieve response
        response = self.request(request_dict)

        # Compare expected response to actual response
        self.compare(response, expected_response_dict)

    def request(self, request_dict):
        """
        @param request_dict: Dictionary with request specs

        Deserializes the ``request_dict``, translates it to an HTTP request
        applied on ``self.client`` , executes the request, and returns the
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
            path, method, data, headers,
        )

        # Execute request and return response object
        return method_mapper[method](path=path, data=data, **headers)

    def compare(self, response, expected_response_dict):
        """
        @param response: HTTPResponse object
        @param expected_response_dict: Dictionary with expected response specs

        Takes the HTTPResponse ``response`` object and deserializes it into a
        dictionary. Then compares it with the expected response dictionary
        """
        # TODO: Be able to count num queries
        # TODO: Be able to compare query types
        # TODO: Be able to compare the response fields, with what I expect.
        # It's challending, given that I need to account for dictionaries and
        # also lists.
        # TODO: Be able to compare the exact response with the expected
        # response
        actual_response_dict = {
            'status_code': response.status_code,
            'headers': {header: response.get(header) for header in expected_response_dict['headers']},
            'data': type(response.content),
            'len': len(response.content),
        }

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
            request = dict(method='GET', path='/api/handler/')
            response = dict(
                status_code=200, data=list, len= 14,
                headers={'content-disposition': 'attachment'},
                num_queries=10,
            )
            self.execute(request, response)

            # another request
            request = {
                    'method': 'POST', 'path': '/api/handler/',
                    'data': {'key': 'value'},
                    'headers': {'content_type': 'application/json'},
            }
            response = {
                    'status_code': 200, 'data': dict, 'len': 14,
                    'headers': {'content-type': 'application/json'},
                    'num_queries':2,
            }
            self.execute(request, response)

