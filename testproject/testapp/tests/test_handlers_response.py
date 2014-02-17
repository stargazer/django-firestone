"""
This module tests the ``firestone.HandlerControlFlow.response`` method
"""
from firestone.handlers import BaseHandler
from django.test import TestCase
from django.test import RequestFactory


class TestResponse(TestCase):
    def test_no_data_and_headers(self):
        handler = BaseHandler()
        request = RequestFactory().get('/')

        res = handler.response('', {})

        self.assertEqual(res.content, '')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['content-type'], 'text/html; charset=utf-8')

    def test_no_headers(self):
        handler = BaseHandler()
        request = RequestFactory().get('/')

        res = handler.response('data', {})

        self.assertEqual(res.content, 'data')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['content-type'], 'text/html; charset=utf-8')

    def test_data_and_headers(self):
        handler = BaseHandler()
        request = RequestFactory().get('/')

        res = handler.response('data', {'content-type': 'application/json'})

        self.assertEqual(res.content, 'data')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['content-type'], 'application/json')

    def test_data_and_extra_headers(self):
        handler = BaseHandler()
        request = RequestFactory().get('/')

        res = handler.response(
            'data', 
            {
                'content-disposition': 'attachment; filename="foo.xls"',
                'content-type': 'application/vnd.ms-excel',
            },
        )

        self.assertEqual(res.content, 'data')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['content-disposition'], 'attachment; filename="foo.xls"')
        self.assertEqual(res['content-type'], 'application/vnd.ms-excel')




    
            

