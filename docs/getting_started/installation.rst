Installation
==============

.. _label-install-for-development-testing:

For Development / Testing
--------------------------------------

Install
^^^^^^^^^^^

Create and activate a virtual environment in which django-firestone will be installed. 
Let's call it ``env``::

        virtualenv env --no-site-packages                        
        cd env
        source bin/activate

Check out the latest version of django-firestone from github and build it::
        
        git clone git@github.com:stargazer/django-firestone.git
        cd django-firestone
        python setup.py install


Test
^^^^^^
Run the complete test suite::

        tox

This runs the testing suite of django-firestone against multiple Python and Django versions and creates a coverage report, which you can access by opening file::

        htmlcov/index.html

To run the test suite quickly against the currently installed Python and Django versions in the virtual environment, run::

        python setup.py test

As a library
-----------------------------------
::
    
    pip install django-firestone

Installing As a Project Dependency
-----------------------------------
Define ``django-firestone`` as a dependency on your project's ``setup.py`` or
``requirements.txt`` file.


