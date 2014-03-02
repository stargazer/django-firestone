[![Build Status](https://travis-ci.org/stargazer/django-firestone.png?branch=master)](https://travis-ci.org/stargazer/django-firestone)
[![Coverage Status](https://coveralls.io/repos/stargazer/django-firestone/badge.png?branch=master)](https://coveralls.io/r/stargazer/django-firestone?branch=master)

# django-fiRESTone

[_Gatorade me bitch_](http://www.youtube.com/watch?v=wNvk4DD1fCU)

## Say what?

REST API Framework, built out of frustration for everything else out there.

## Goal

### First iteration

Write a very simple, well-documented and extensible API framework. I want to lay out the basic data flow with limited functionality, mainly to 
test my design ideas.

* Base and Model handlers
* CRUD operations
* Deserialize JSON request body
* Serialize response data to JSON
* Request-level field selection
* Handlers should declare everything cleanly and with little code
* Session Authentication
* 100% test coverage

### Second iteration

* Think of authentication and authorization
 * Multiple authentication methods per handler
 * Does it make more sense to define authentication method per HTTP method, for each handler? For example, 
   have a decorator for each action method view that defines whether this requires an authentication, and if yes, which one.
* More authentication methods - Http Signature authentication
* Enable/disable BULK-POST, Plural-PUT and Plural-DELETE explicitly
* Ordering, slicing, filtering   
* ModelHahdler should be able to output fake fields
* CSRF protection

## Design decisions

* ``django-firestone`` makes use of class based-views*. This means that:
 * API Handlers are more modular and very easily testable
 * They inherit from each other and therefore reduce boilerplate code
 * Every step in the request data flow, from start to finish, can be easily
   overridden and extended.

* Multiple handlers can be assigned per resource type, with each handler being
  responsible for a specific authentication mechanism. This way multiple
  control flow statements and spaghetti code in the handlers is avoided.

* Every handler specifies the representation of its own response, including
  that of nested fields, regardless of how deep they appear.

* For now, only accepts ``content-type: application/json``, and returns
  ``application/json`` responses. I will soon extend it to other serialization
  formats.

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

## Life Cycle of a Request

    request    --> URL Mapper invokes the corresponding proxy view based on the URL
    Proxy view --> invokes the corresponding handler, based on the request's authentication method
    Handler    --> Executes the request and returns an HTTPResponse object to the proxy view
    Proxy view --> Returns the HttpResponse object

## Reserved querystring parameters

* ``field``, for field selection
* ``order``, for ordering
* ``page``, ``ipp``(items per page) for paging

## Ordering
Initiated by the ``order=`` querystring parameter. It only makes sense for
plural GET, plural PUT and plural DELETE requests. For all other requests it's
ignored.

## Pagination
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

## Requirements

* Python 2.7
* Django 1.5.4

## How to install

For now, clone github repository. Soon available on PyPi.

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

## Tests

The ``testproject`` package contains a mini Django application built on top of
``django-firestone``. The test project is mainly used to initiate
``django-firestone``'s test suite

	python bootstrap.py 
	bin/buildout

In order to run the tests:

	bin/test

In order to run the tests and get a test coverate report, run:

    bin/createcoverage

You will get an HTML report in ``htmlcov/index.html`` with all details.

## Resources

* [django-preserialize](https://github.com/bruth/django-preserialize)
* [Classy Class Based Views](http://ccbv.co.uk/)
* [HTTP status codes](http://www.restapitutorial.com/httpstatuscodes.html)

## Improvements compared to django-icetea

Errors - Clear and readable error messages
Serialization - Every handler is solely responsible for the representation of its own output. That includes nested data structures, no matter how deeply nested they are
Lots of handlers can be declared per resource, with each one responsible for one auth method. This greatly reduces control flow statements on application level
Allowed fields for POST and PUT requests can be specified differently
