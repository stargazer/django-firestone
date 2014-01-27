# django-fiRESTone

[Gatorade me bitch](http://www.youtube.com/watch?v=wNvk4DD1fCU)

REST API framework

## Design decisions

* The handlers/views that ``django-firestone`` exposes, make use of ``Django``'s *class-based views*. Why?
 * Handlers are more modular and very easily testable
 * They can be built upon the abstractions that the ``django.views.generic`` collection offers and therefore reduce boilerplate code
 * They can inherit from each other
 * Every step in the request data flow, from start to finish, can be easily overridden.

* For now, only accepts ``content-type: application/json``, and returns ``application/json``. 
  It is however very easy to extend to other serialization format. It's on my near-future todo list.

## Goal

### First iteration

Write a very simple, well-documented and extensible API framework. I want to lay out the basic data flow with limited functionality, mainly to 
test my design ideas.

* Create Base and Model handler
* Handlers should be able to serialize their output to a pure python data
  structure and then to json. 
* Request-level field selection
* Deserialize request body
* CRUD operations
* Handlers should declare everything cleanly and with little code
* Easily testable
* Accepts and returns only json data

### Second iteration

* Think of authentication and authorization
 * Multiple authentication methods per handler
 * Does it make more sense to define authentication method per HTTP method, for each handler? For example, 
   have a decorator for each action method view that defines whether this requires an authentication, and if yes, which one.
* Ordering, slicing, filtering   

## Requirements

* Python 2.7
* Django 1.5.4

## Tests

The ``tests`` package contains a Django application that tests many of django-firestone's features. 
In order to build the application:

	python bootstrap.py -v 2.1.1
	bin/buildout

In order to run the tests:

	bin/test

## Resources

* [django-preserialize](https://github.com/bruth/django-preserialize)
* [Classy Class Based Views](http://ccbv.co.uk/)
* [HTTP status codes](http://www.restapitutorial.com/httpstatuscodes.html)


