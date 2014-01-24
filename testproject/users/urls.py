from django.conf.urls import *
from handlers import UserHandler

urlpatterns = patterns('',
    url(r'^users/$', UserHandler.as_view()),
)
