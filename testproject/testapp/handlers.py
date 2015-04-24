from firestone.handlers import BaseHandler
from firestone.authentication_mixins import NoAuthenticationMixin
from django.http import HttpResponse


class TestHandler(BaseHandler, 
                  NoAuthenticationMixin):
    def get(self, request, *args, **kwargs):
        return HttpResponse('GET')

    def post(self, request, *args, **kwargs):
        return HttpResponse('POST')



