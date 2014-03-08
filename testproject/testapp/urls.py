from django.conf.urls import *
from firestone.proxy import Proxy
from handlers import DataHandler
from handlers import UserHandlerSessionAuth
from handlers import UserHandlerNoAuth

datahandler_proxy = Proxy(DataHandler)
userhandler_proxy = Proxy(UserHandlerSessionAuth, UserHandlerNoAuth)

urlpatterns = patterns('',
    url(r'^data/$', datahandler_proxy),
    url(r'^users/$', userhandler_proxy),
    url(r'^users/(?P<id>[^/]+)/$', userhandler_proxy),
)
