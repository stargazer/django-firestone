# django-gatorade

[Gatorade me bitch](http://www.youtube.com/watch?v=wNvk4DD1fCU)

REST API framework

Accepts ``content-type: application/json``, and returns ``application/json``

Good example of Rest API status codes. Keeping it here for future reference:
http://www.restapitutorial.com/httpstatuscodes.html

## Goal

Write a very simple and well documented Rest API framework. API handlers are
based on Django's class based view, and therefore inherit their flexibility and
power.

On the first
iteration, I simply want to make it plain and clear. No fancy stuff, just very
clear abstractions that enables the construction of very neatly written API
handlers.

First iteration
* Create Base and Model handler
* Handlers should be able to serialize their output to a pure python data
  structure and then to json. 
* Request-level field selection
* Deserialize request body
* CRUD operations
* Handlers should declare everything cleanly and with little code
* Easily testable
* Accepts and returns only json data
* Examine the use of class based views (see exactly what ``dispatch`` does). 
  Can they indeed minimize the code I need to write?

Second iteration
* Each handler defines strictly what http methods it supports
* Be able to define multiple authentication methods per handler

## Requirements

* Python 2.7
* Django 1.5.4

## Running tests

The ``tests`` package contains a Django application that tests many of django-gatorade's features. 
In order to build the application:

	python bootstrap.py -v 2.1.1
	bin/buildout

In order to run the tests:

	bin/test

## Useful packages to look into
* django-preserialize: https://github.com/bruth/django-preserialize
Especially section ``conventions`` might be a very good idea about how to
define fields in handlers.
Every model handler should define it's output template. For any nested fields
which would be included in its response, the handler should define their
profiles.
So, every handler will exactly select how its representation is going to be.



