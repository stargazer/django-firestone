Design
=================

When first designing django-firestone, the idea was to build it around Django's
generic Class-Based Views(CBVs). It was however proven that, even though they are
indeed very powerful and cover numerous use cases, they are very inflexible.
They enforce a very fixed data flow, which simply doesn't fit in some
architectures.

Take the following example:

Upon request to an API url endpoint, I wanted to invoke a very generic proxy
view, perform some very generic checks, and eventually call the *real* view
(which from now on, I will call *handler*) for the actual request processing.
When trying to fit this into Django's CBVs, I had the following problem; the
view's ``dispatch`` method immediately tries to call the view method
corresponding to the request's HTTP verb. In my case, this method would
live in the handler(a separate class), not in the view class itself. Having this
separation buys a lot of flexibility and it's one of the initial design
decisions. And it is of course not possible using Django's generic CBVs.

Yes, I could override ``django.views.generic.base.View.dispatch`` and have it behave accordingly, 
but that would basically mean that I override the whole logic of Django's generic CBVs. 
For this reason, I chose to start from scratch; Same paradigm, different logic and implementation.

So, in django-firestone I have the initial view that the URL mapper invokes,
(let's call it *proxy view* from now on). This class is separate from
the handler class, which does the heavylifting of the request processing. This
separation allows the proxy view to perform some generic checks, and then
select and instantiate the appropriate handler(according to the request's
authentication method), and invoke the relevant method
to kick-off the request processing. The handler instance lives for as long as the
request is processed, and then dies. 

This logic would be impossible to have with Django's build-in CBVs. In order to
implement this, one would need to fascilitate all authentication methods within
the same view class, litter the code with control flow statement on each step
checking for the authentication method the request uses, and eventually getting a big fat
headache.

As for django-firestone; Do you need to expose a resource using different
authentication methods? Easy. Create as many handlers as the authentication
methods you need to support, assign the corresponding authentication method to
every handler, and you are done. The proxy view will control when each handler
gets called. No control flow statements, no spaghetti code.

To summarize, django-firestone using class based-views means:

* API Handlers are modular and very easily testable
* Every step in the request data flow, from start to finish, can be easily overridden and extended.
* Handler classes inherit from each other. As a result, the boilerplate code is reduced
* Multiple handlers can be assigned per resource type. 
  Each handler is responsible for a specific authentication method. 
  This way the handlers remain clean and don't get polluted with control flow statements and spaghetti code
