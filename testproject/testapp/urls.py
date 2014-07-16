from django.conf.urls import *
from firestone.proxy import Proxy
from handlers import DataHandler
from handlers import UserHandlerSessionAuth
from handlers import UserHandlerNoAuth
from handlers import ContactHandlerSessionAuth

datahandler_proxy = Proxy(DataHandler)
userhandler_proxy = Proxy(UserHandlerSessionAuth, UserHandlerNoAuth)
contacthandler_proxy = Proxy(ContactHandlerSessionAuth)

urlpatterns = patterns('',
    url(r'^data/$', datahandler_proxy),
    
    url(r'^users/$', userhandler_proxy),
    url(r'^users/(?P<id>[^/]+)/$', userhandler_proxy),
    
    url(r'^contacts/$', contacthandler_proxy),
    url(r'^contacts/(?P<id>[^/]+)/$', contacthandler_proxy),

)
