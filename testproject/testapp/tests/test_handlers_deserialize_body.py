"""
This module tests method ``firestone.handlers.BaseHandler.deserialize_body``
"""
from firestone.handlers import BaseHandler
from firestone import exceptions
from django.test import TestCase
from django.test import RequestFactory
import json


def init_handler(handler, request, *args, **kwargs):
    handler.request = request
    handler.args = args
    handler.kwargs = kwargs
    return handler


class TestDeserializeBody(TestCase):
    def test_valid_json(self):
        request_body = """
        {
            "key": "value"
        }
        """

        request = RequestFactory().post(
            '/',
            data=request_body,
            content_type='application/json'
        )
        handler = init_handler(BaseHandler(), request)

        # Deserialize request body
        handler.deserialize_body()

        self.assertEqual(
            handler.request.data,
            json.loads(request_body),
        )

    def test_invalid_json(self):
        request_body = """
        {
            "key":
        }
        """

        request = RequestFactory().post(
            '/',
            data=request_body,
            content_type='application/json',
        )
        handler = init_handler(BaseHandler(), request)

        self.assertRaises(
            exceptions.BadRequest,                
            handler.deserialize_body,
        )

    def test_invalid_content_type(self):
        request_body = """
            <xml>
                <node>
                    value
                </node>
            </xml>
        """

        request = RequestFactory().post(
            '/',
            data=request_body,
            content_type='application/xml',
        )
        handler = init_handler(BaseHandler(), request)

        self.assertRaises(
            exceptions.UnsupportedMediaType,
            handler.deserialize_body,
        )


