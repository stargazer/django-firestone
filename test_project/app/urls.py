from django.conf.urls import *
from test_project.app.views import TestAPIView


urlpatterns = patterns('',
    url(r'^testapiview/$', TestAPIView.as_view()),
)    
