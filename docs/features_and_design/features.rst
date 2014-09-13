Features
===========

django-firestone offers the following features:

* Creation and mapping of API handlers to Django models
* Creation of generic non-model API handlers
* CRUD operations out of the box
* Multiple authentication methods
  
  * Session-based 
  * Signatures
  * JSON Web Tokens

* Mapping multiple handlers per resource, with each handler having a different authentication method
* Flexible output representation, and the ability to provide detailed
  representation of all nested data structures, no matter how deep they appear
* Request-level field selection
* Acceptable Request Content-types:
  
  * ``application/json``
  * ``application/x-www-form-urlencoded``   

* Response serialization in:
  
  * ``application/json``
  * ``application/vnd.ms-excel``

* Filtering, ordering, pagination
* Fully extendible and customizable

