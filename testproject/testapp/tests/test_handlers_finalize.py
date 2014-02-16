"""
This module tests the ``firestone.handlers.HandlerControlFlow.finalize`` method
"""
from firestone.handlers import BaseHandler
from firestone.handlers import ModelHandler
from django.test import TestCase
from django.test import RequestFactory
from django.contrib.admin.models import LogEntry
from model_mommy import mommy

class TestBaseHandlerFinalize(TestCase):
    def setUp(self):
        self.handler = BaseHandler()
        self.request = RequestFactory().delete('/')

        self.logentries = mommy.make(LogEntry, 10)

    def test_result(self):
        """
        Do the data indeed get deleted?
        """
        data = LogEntry.objects.all()
        self.handler.finalize(data, self.request)
        
        self.assertEqual(LogEntry.objects.count(), 0)

    def test_query_count(self):
        data = LogEntry.objects.all()
        self.assertNumQueries(
            1,
            self.handler.finalize,
            data, self.request,
        )


class TestModelHandlerFinalizeSingular(TestCase):
    def setUp(self):
        self.handler = ModelHandler()
        self.handler.model = LogEntry
        self.request = RequestFactory().delete('/')

        self.logentry = mommy.make(LogEntry)

    def test_result(self):
        data = self.logentry
        self.handler.finalize(data, self.request, id=self.logentry.id)

        self.assertEqual(LogEntry.objects.count(), 0)

    def test_query_count(self):
        data = self.logentry
        self.assertNumQueries(
            1,
            self.handler.finalize,
            data, self.request, id=self.logentry.id,
        )


class TestModelHandlerFinalizePlural(TestCase):
    def setUp(self):
        self.handler = ModelHandler()
        self.handler.model = LogEntry
        self.request = RequestFactory().delete('/')

        self.logentries = mommy.make(LogEntry, 10)

    def test_result(self):
        data = LogEntry.objects.all()
        self.handler.finalize(data, self.request)

        self.assertEqual(LogEntry.objects.count(), 0)

    def test_query_count(self):
        data = LogEntry.objects.all()
        self.assertNumQueries(
            1,
            self.handler.finalize,
            data, self.request
        )

