from django.conf.urls import *
from firestone.proxy import Proxy
from handlers import UserHandlerSessionAuth
from handlers import UserHandlerNoAuth


userhandler_proxy = Proxy(UserHandlerSessionAuth, UserHandlerNoAuth)

urlpatterns = patterns('',
    url(r'^users/$', userhandler_proxy),
    url(r'^users/(?P<id>[^/]+)/$', userhandler_proxy),
)
