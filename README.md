[![Build Status](https://travis-ci.org/stargazer/django-firestone.png?branch=master)](https://travis-ci.org/stargazer/django-firestone)
[![Coverage Status](https://coveralls.io/repos/stargazer/django-firestone/badge.png?branch=master)](https://coveralls.io/r/stargazer/django-firestone?branch=master)
[![Downloads](https://pypip.in/download/django-firestone/badge.svg)](https://pypi.python.org/pypi/django-firestone/)
[![Latest Version](https://pypip.in/v/django-firestone/badge.png)](https://pypi.python.org/pypi/django-firestone/)


# django-firestone

REST API Framework. Modular, extendible and addressing lots of the limitations
that I came across using other frameworks.

### Principles

* Based on Django's Class-based views
* No strict data flow is enforced
* Its building blocks are standalone mixins which the views can subclass and inherit their behavior.

### How to install

    pip install django-firestone

### How to use

Create your Class-based view and inherit from firestone's ``APIView`` class
```python
# views.py
from firestone.views import APIView
from django.http import HttpResponse


class MyAPIView(APIView):
def get(self, request, *args, **kwargs):
    return HttpResponse('Hi')
```

Define the view in the URL dispatcher
```python
# urls.py
from django.conf.urls import *
from views import MyAPIView


urlpatterns = patterns('',
    url(r'^myapiview/$', MyAPIView.as_view()),
)    
```

#### Deserialization

``django-firestone`` uses the [``django-deserializer``](https://github.com/stargazer/django-deserializer) module to deserialize the request body. ``django-deserializer`` provides the mixin ``DeserializerMixin``. Our API views can subclass this mixin, inherit its functionality and easily use it.

```python
from firestone.views import APIView
from deserializer.mixins import DeserializerMixin
from django.http import HttpResponse

class MyAPIView(APIView,
                DeserializerMixin):

    def post(self):
        body = self.deserialize()
        ...
        ...
```
            
