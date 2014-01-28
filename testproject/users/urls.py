from django.conf.urls import *
from firestone.views import View
from handlers import UserHandlerDjangoAuth
from handlers import UserHandlerNoAuth


userhandler_view = View(UserHandlerDjangoAuth, UserHandlerNoAuth)

urlpatterns = patterns('',
    url(r'^users/$', userhandler_view),
    url(r'^users/(?P<id>[^/]+)/$', userhandler_view),
)
