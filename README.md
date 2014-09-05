[![Build Status](https://travis-ci.org/stargazer/django-firestone.png?branch=master)](https://travis-ci.org/stargazer/django-firestone)
[![Coverage Status](https://coveralls.io/repos/stargazer/django-firestone/badge.png?branch=master)](https://coveralls.io/r/stargazer/django-firestone?branch=master)
[![Downloads](https://pypip.in/download/django-firestone/badge.svg)](https://pypi.python.org/pypi/django-firestone/)
[![Latest Version](https://pypip.in/v/django-firestone/badge.png)](https://pypi.python.org/pypi/django-firestone/)


# django-firestone

REST API Framework. Modular, extendible and addressing lots of the limitations
that I came across using other frameworks.



## Goals

### Currently accomplished
* Base and Model handlers
* CRUD operations
* Accepts ``application/json`` and ``application/x-www-form-urlencoded`` content-type and returns JSON
* Request-level field selection
* Multiple authentication methods
* Multiple handlers should be able to to serve the same resource, with each
  using a different authentication method.
* Ordering, slicing, filtering   
* ModelHahdler should be able to output fake fields. Static model related data can be
  added by using properties. Dynamic model related data can be added by
  using the handler's ``inject_data_hook`` method, which, since is a handler
  method, is aware of the request context.
* Enable/disable Plural-PUT and Plural-DELETE explicitly. 
* View that handles login with username/password and returns JWT token
* Emails upon crashes
* Excel serialization

### TODO
* Rename methods that should be renamed. Methods that return something should
  be named ``get-<something>``. Others should be named ``set-<something>``.
* Be able to exclude model fields from validation and cleaning
* Check all TODOs in the code
* Make sure code is succinct and it's flow is understandable.
* Flexible way to add headers and specify status codes to responses
* http://pycallgraph.slowchop.com/en/master/index.html
* 100% test coverage
* Rate limiting
* PEP8



## Design decisions

* ``django-firestone`` makes use of class based-views. This means that:
 * API Handlers are modular and very easily testable
 * Every step in the request data flow, from start to finish, can be easily
   overridden and extended.
 * They inherit from each other, and therefore reduce boilerplate code

* Multiple handlers can be assigned per resource type, with each handler being
  responsible for a specific authentication mechanism. This way multiple
  control flow statements and spaghetti code in the handlers is avoided.

* Every handler specifies the representation of its own response, including
  that of nested fields, regardless of how deep they appear.



## A few words on Django's class-based views (CVBs).

I initially started building ``django-firestone`` on top of Django's generic
CBVs. Even though these are indeed very powerful and cover various use cases,
have proven to be very inflexible. They enforce a very fixed data flow, which
didn't suit the architecture of ``django-firestone`` at all.

Take the following example:

> I needed a very generic _proxy view_ to perform some checks and then invoke the real view
> (which I will call ``handler`` from now on) for all the request processing.
> However, the ``dispatch`` method of Django's generic class-based views wants
> to immediately call the view method corresponding to the HTTP request method.
> In my case, this method would live in the handler, and not in the view. Yes,
> I could override ``django.views.generic.base.View.dispatch``, but that would
> basically mean that I override the whole logic of Django's generic CBVs. So I
> chose to start from scratch; Same paradigm, different logic and
> implementation.

The use of proxy views, allows ``django-firestone`` to select the correct
handler based on the authentication method that a request uses. This makes
for way cleaner handler code, without any flow control checks that would
otherwise be needed. 
Need to expose a model resource, using multiple authentication methods? You'd
then need create as many handlers, with each one responsible for each
authentication method.



## Requirements

* Python 2.7
* Django 1.5.4 or later



## Life Cycle of a Request

    request    --> URL Mapper invokes the corresponding proxy view based on the URL
    Proxy view --> invokes the corresponding handler, based on the request's authentication method
    Handler    --> Executes the request and returns an HTTPResponse object to the proxy view
    Proxy view --> Returns the HttpResponse object



## Authentication

### How?

The handler parameter ``authentication`` defines the authentication method used
for that particular handler class. The authentication method can be any of the 
mixins defined in the ``firestone.authentication`` module.

While the authentication method is defined as a handler class attribute, behind the
scenes it's set as a handler class mixin, therefore the handler class inherits
its funcionality.

### Authentication Mixins

#### NoAuthentication
The API handler is open and allows all incoming requests

#### SessionAuthentication
The API handler only allows requests with a valid session ID

#### SignatureAuthentication
The API handler only allows requests that carry a valid signature 

#### JWTAuthentication (JSON Web Token Authentication)
The API handler only allows requests that carry a valid ``Authentication: JWT
<token>`` header.

A Token can be issued using the ``pyJWT`` libraryJWT, upon correct user
login. You can directly use the
``firestone.example_handlers.ObtainJWTHandler``, or even modify/extend it.

Once you login and obtain a JWT token, you can use the token in the
``Authorization`` request header for any handler that uses JWT Authentication, as:

    Authorization: JWT <token>

In case you'd like to modify how a user is identified and the ``request.user``
parameter is set, for handlers using JWT Authentication, override handler
method ``verify_request_user(payload)``.

Provide a few links that explain it well. 
How to customize behavior.
Which HTTPS it's rock solid, and has many benefits compared to sesssions.


## Handler specifics

### Reserved querystring parameters

* ``field``, for field selection
* ``order``, for ordering
* ``page``, ``ipp``(items per page) for paging

### Filtering
TODO

### Ordering
Initiated by the ``order=`` querystring parameter. It only makes sense for
plural GET, plural PUT and plural DELETE requests. For all other requests it's
ignored.

### Pagination
Initiated by the ``page=`` querystring parameter. The ``ipp=`` querystring 
parameters indicates the items per page. If not given, the handler's default     
``items_per_page`` attribute is used.
It only makes sense on requests that return a list of data, and for all other 
requests is ignored.

Pagination is performed after the action takes place, and this is mainly the
reason that it should never raise an error. In that case, the resources
modified/created would be hidden from the response.

Careful, for requests like a plural DELETE, plural PUT, or bulk POST, pagination can be
confusing, since it could hide part of the resources that have been
created/deleted/updated.



## How to install ``django-firestone``

### For development or experimenting 

#### Create a virtual environment and clone ``django-firestone``

    virtualenv folder --no-site-packages
    cd folder
    source bin/activate
    git clone git@github.com:stargazer/django-firestone.git
    cd django-firestone

#### Install it

    python setup.py install

#### Run test suite

    python setup.py test

#### Generate test coverage report    
    
    coverage run setup.py test
    coverage html

#### Play with the test project ``testproject``

    ./manage.py <management command>

### As a dependency on another project
either run:

    pip install django-firestone

or include in the requirements of your project ``django-firestone``

## Tests

The ``testproject`` package contains a mini Django application built on top of
``django-firestone``. The test project is mainly used to initiate
``django-firestone``'s test suite

### Run the full testing suite

Clone django-firestone
    
    git clone git@github.com:stargazer/django-firestone.git    

Install tox and run

    pip install tox coverage
    cd django-firestone
    tox

This will run the whole testing suite, accounting for various combinations of
Python and Django versions



## How to use

    # handlers.py
    from firestone import ModelHandler
    from authentication import SessionAuthentication, NoAuthentication
    class UserHandlerSessionAuth(ModelMandler):
        """
        This handler will take over requests carrying a Django session
        """
        model = User
        authentication = SessionAuthentication
        http_methods = ['GET', 'POST']

    class UserHandlerNoAuth(ModelHandler):
        """
        This handler will take over non-authenticated requests
        """
        model = User
        authentication = NoAuthentication
        http_methods = ['GET',]

    # urls.py
    from django.conf.urls import *
    from firestone.proxy import Proxy
    from handlers import UserHandlerSessionAuth, UserHandlerNoAuth

    userhandler_proxy = Proxy(UserHandlerSessionAuth, UserHandlerNoAuth)

    urlpatterns = patterns('',
        url(r'^users/$', userhandler_proxy),
    )



## Resources

* [django-preserialize](https://github.com/bruth/django-preserialize)
* [Classy Class Based Views](http://ccbv.co.uk/)
* [HTTP status codes](http://www.restapitutorial.com/httpstatuscodes.html)



## Improvements compared to django-icetea

* Authentication - More authentication methods
* Errors - Clear and readable error messages
* Serialization - Every handler is solely responsible for the representation of its own output. That includes nested data structures, no matter how deeply nested they are
* Lots of handlers can be declared per resource, with each one responsible for one auth method. This greatly reduces control flow statements on application level
* Allowed request body fields for POST and PUT requests can be specified differently
