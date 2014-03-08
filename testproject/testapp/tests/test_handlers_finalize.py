"""
This module tests the ``firestone.handlers.HandlerControlFlow.finalize`` method
"""
from firestone.handlers import BaseHandler
from firestone.handlers import ModelHandler
from django.test import TestCase
from django.test import RequestFactory
from django.contrib.admin.models import LogEntry
from model_mommy import mommy

def init_handler(handler, request, *args, **kwargs):
    # Mimicking the initialization of the handler instance
    handler.request = request
    handler.args = args
    handler.kwargs = kwargs
    return handler


class TestBaseHandlerFinalize(TestCase):
    def setUp(self):
        request = RequestFactory().delete('/')
        handler = init_handler(BaseHandler(), request)
        self.handler = handler

        self.logentries = mommy.make(LogEntry, 10)

    def test_result(self):
        """
        Do the data indeed get deleted?
        """
        data = LogEntry.objects.all()
        handler = self.handler
        handler.finalize(data)
        
        self.assertEqual(LogEntry.objects.count(), 0)

    def test_query_count(self):
        handler = self.handler
        data = LogEntry.objects.all()
        self.assertNumQueries(
            1,
            self.handler.finalize,
            data,
        )


class TestModelHandlerFinalizeSingular(TestCase):
    def setUp(self):
        request = RequestFactory().delete('/')
        handler = init_handler(ModelHandler(), request)
        handler.model = LogEntry
        self.handler = handler

        self.logentry = mommy.make(LogEntry)

    def test_result(self):
        handler = self.handler
        handler.kwargs = {'id': self.logentry.id}
        data = self.logentry
        handler.finalize(data)

        self.assertEqual(LogEntry.objects.count(), 0)

    def test_query_count(self):
        handler = self.handler
        handler.kwargs = {'id': self.logentry.id}

        data = self.logentry
        self.assertNumQueries(
            1,
            self.handler.finalize,
            data
        )


class TestModelHandlerFinalizePlural(TestCase):
    def setUp(self):
        request = RequestFactory().delete('/')
        handler = init_handler(ModelHandler(), request)
        handler.model = LogEntry
        self.handler = handler

        self.logentries = mommy.make(LogEntry, 10)

    def test_result(self):
        handler = self.handler
        data = LogEntry.objects.all()
        handler.finalize(data)

        self.assertEqual(LogEntry.objects.count(), 0)

    def test_query_count(self):
        handler = self.handler
        data = LogEntry.objects.all()
        self.assertNumQueries(
            1,
            self.handler.finalize,
            data,
        )

