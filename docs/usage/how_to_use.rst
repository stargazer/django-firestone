How to Use
==============

Let's say we have an app *contacts* with a model like this::

        # models.py

        from django.db import models
        from django.contrib.auth.models import User

        class Contact(models.Model):
            owner = models.ForeignKey(User)
            name = models.CharField(max_length=32)
            surname = models.CharField(max_length=32)

We need to create an API handler, to expose this model through a REST API::

        # handlers.py

        from firestone.handlers import ModelHandler
        from firestone.authentication import SessionAuthentication
        from models import Contact


        class ContactHandler(ModelHandler):
            model = Contact
            http_methods = ['GET',]
            authentication = SessionAuthentication

            user_template = {
                'fields': ['id', username',]
            }
            template = {
            'fields': ['owner', 'name', 'surname'],
            'related': {
                'owner': user_template
            }

Let's adjust the url mapper and tie the handler to some URL endpoint::

        # urls.py

        from handlers import ContactHandler
        from firestone.proxy import Proxy
        from django.conf.urls import *

        contacthandler_proxy = Proxy(ContactHandler)

        urlpatterns = patterns('',
            url(r'^contacts/$', contacthandler_proxy),
        )

Now if you run the application, any session-authenticated GET request to the url ``/contacts/`` will return all Contact instances.        
