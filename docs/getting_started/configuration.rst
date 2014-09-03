Configuration
===============

Django Application *settings* parameters
----------------------------------------

**EMAIL_CRASHES**

    If set to ``True``, and at the same time ``DEBUG=False``, emails will be sent to the administrators upon server crashes. Default value is ``False``. 

    Requires valid values for the following parameters:

        * ADMINS
        * EMAIL_HOST
        * EMAIL_PORT
        * EMAIL_HOST_USER
        * EMAIL_HOST_PASSWORD

    example::

        EMAIL_CRASHES = True
        DEBUG = False
        ADMINS = (
            ('First Aid', 'admin@example.com')
        )
        EMAIL_HOST = 'smtp.sendgrid.net'
        EMAIL_PORT = 587
        EMAIL_HOST_USER = '<email service username>'
        EMAIL_HOST_PASSWORD = '<email service password>'


    If ``DEBUG=True``, crash reports will be included in the response, regardless of the value of ``EMAIL_CRASHES``.
