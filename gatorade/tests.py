from django.test import TestCase
from django.test import Client 
import json

class BaseTest(TestCase):
    """
    Very flexible testing class for testing API handlers.

    https://docs.djangoproject.com/en/1.5/topics/testing/overview/
    """
    def setUp(self):
        self.client = Client(HTTP_CONTENT_TYPE='application/json')
        self.login()

    def login(self):
        self.client.login(
            username=self.USERNAME,
            password=self.PASSWORD,
        )

    def verify(self, response, **kwargs):
        """
        Runs through the response object, and verifies that it matches the
        expected response.
        """
        # TODO: Be able to count num queries
        # TODO: Be able to compare the exact response with the expected
        # response
        expected_response_data = {
            'status_code': kwargs.get('status_code'),
            'headers': kwargs.get('headers'),
            'content_data_structure': kwargs.get('content_data_structure'),
            'content_num': kwargs.get('content_num')
            #'num_queries': kwargs.get('num_queries'),
        }

        actual_response_data = {
            'status_code': response.status_code,
            'headers': {header: response.get(header) for header in expected_response_data[headers]},
            'content_data_structure': type(response.content),
            'content_num': len(response.content),
            #'num_queries':
        }                
        
        for param in ('status_code', 'content_data_structure', 'content_num'):
            self.assertEqual(actual_response_data(param), expected_response_data[param])
        if expected_response_data.get('headers'):
            for header, value in expected_response_data['headers'].items():
                self.assertEqual(actual_response_data[header], value)


# Example of an application-level test class.
class HandlerTest(BaseTest):
        USERNAME = 'tester@example.com'
        PASS     = 'pass'

        fixtures = []

        # This is an application level test method            
        def test_method_name(self):         
            # one request
            response = self.client.get('/api/handler/')
            self.verify(response,
                status_code=200,
                content_data_structure=list,
                content_len=14,
                headers={'content-disposition': 'attachment'},
                num_queries=10,
            )

            # another request
            response = self.client.post(
                'v1/handler/',
                json.dumps(dict(key=value)),
                content_type='application/json',
            )
            self.verify(response,
                status_code=200,
                content_data_structure=dict,
                content_len=10,
                headers={'content-type': 'application/json'},
                num_queries=2,
            )

