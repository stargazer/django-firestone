# django-gatorade

[Gatorade me bitch](http://www.youtube.com/watch?v=wNvk4DD1fCU)

REST API framework

Accepts ``content-type: application/json``, and returns ``application/json``

Good example of Rest API status codes. Keeping it here for future reference:
http://www.restapitutorial.com/httpstatuscodes.html

## Goal

Write a very simple and well documented Rest API framework. On the first
iteration, I simply want to make it plain and clear. No fancy stuff, just very
clear abstractions that enables the construction of very neatly written API
handlers.

First iteration
* Create Base and Model handler
* Handlers should be able to output fields, request body
  fields, and crud operations they support
* Handlers should declare everything cleanly and with little code
* Easily testable
* Accepts and returns only json data

Second iteration
* Be able to define multiple authentication methods per handler
* Per request field selection

## Requirements

* Python 2.7
* Django 1.5.4

## Useful packages to look into
* django-preserialize: https://github.com/bruth/django-preserialize
Especially section ``conventions`` might be a very good idea about how to
define fields in handlers.
Every model handler should define it's output template. For any nested fields
which would be included in its response, the handler should define their
profiles.
So, every handler will exactly select how its representation is going to be.


