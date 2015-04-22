Testing
===========

Full test suite
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In order to run the whole testing suite, against all supported configurations, you need to install ``tox`` on a system-wide level::

        pip install tox
        
``tox`` builds its own ``virtualenv`` for every configuration it tests against,
so don't activate any ``virtualenv``.

Checkout django-firestone::

        git clone git@github.com:stargazer/django-firestone.git
        cd django-firestone
        
Run tox::
        
        tox

To create a coverage report, run::

        coverage html

and view it by opening file::

        htmlcov/index.html

Run the tests against a ``virtualenv`` configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
While in a ``virtualenv``, run::

        python setup.py test

