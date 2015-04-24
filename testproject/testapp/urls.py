from django.conf.urls import *
from testproject.testapp.handlers import TestHandler


urlpatterns = patterns('',
    url(r'^testhandler/$', TestHandler.as_view()),
)    
