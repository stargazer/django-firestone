from django.test import TestCase
from django.test import Client 

class BaseTest(TestCase):
    """
    Very flexible testing class for testing API handlers.
    """
    def setUp(self):
        self.client = Client(HTTP_CONTENT_TYPE='application/json')
        self.login()

    def login(self):
        self.browser.login(
            username=self.USERNAME,
            password=self.PASSWORD,
        )

    def verify(self, response, **kwargs):
        """
        Runs through the response object, and verifies that it matches the
        expected response.
        """
        if kwargs.get('content_type'):
            self.assertEqual(
                type(response.content, 
                kwargs.get['content_type']
            )
        if kwargs.get('content_num'):
            self.assertEqual(
                len(response.content,
                kwargs.get('content_num'),
            )
        if kwargs.get('headers'):
            for header, value in kwargs.get('headers').items():
                assertEqual(
                    response.headers[header],
                    value,
                )
        if kwargs.get('num_queries'):
            # TODO: Check if there's a way to obtain the DB query number
            pass


# Example of an application-level test class.
class HandlerTest(BaseTest):
        USERNAME = 'tester@example.com'
        PASS     = 'pass'

        # This is an application level test method            
        def test_method_name(self):         
            # one request
            response = self.client.get('/api/handler/')
            self.verify(response,
                content_type=list,
                content_num=14,
                headers={'content-disposition': 'attachment'},
                num_queries=10,
            )

            # another request
            response = self.client.post(
                'v1/handler/',
                dict(key=value),
                content_type='application/json',
            )
            self.verify(response,
                content_type=dict,
                content_num=10,
                headers={'content-type': 'application/json'},
                num_queries=2,
            )

