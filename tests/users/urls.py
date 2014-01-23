from django.conf.urls import *
from handlers import AccountHandler

urlpatterns = patterns('',
    url(r'^users/$', AccountHandler.as_view()),
)
