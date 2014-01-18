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
        expected_status_code=kwargs.get('status_code')
        expected_headers=kwargs.get('headers')
        expected_content_type=kwargs.get('content_type')
        expected_content_num=kwargs.get('content_num')
        expected_num_queries=kwargs.get('num_queries')
        
        response_status_code = response.status_code
        response_content = json.loads(response.content)
        response_headers = {header: response.get(header) for header in expected_headers}

        if expected_status_code:
            self.assertEqual(response_status_code, expected_status_code)
        if expected_content_type:
            self.assertEqual(type(response_content), expected_content_type)
        if expected_content_num
            self.assertEqual(len(response_content), expected_content_num)
        if expected_headers:
            for header, value in expected_headers.items():
                self.assertTrue(response_headers[header], value)
        if expected_num_queries:
            # TODO: Check if there's a way to obtain the DB query number
            pass
                                    

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
                content_type=list,
                content_num=14,
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
                content_type=dict,
                content_num=10,
                headers={'content-type': 'application/json'},
                num_queries=2,
            )

