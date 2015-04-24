from firestone.views import APIView
from firestone.authentication_mixins import NoAuthenticationMixin
from deserializer.mixins import DeserializationMixin
from django.http import HttpResponse


class TestAPIView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse('GET')

    def post(self, request, *args, **kwargs):
        body = self.deserialize()
        return HttpResponse('POST: Got %s' % body)



