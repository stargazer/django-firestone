from django.conf.urls import patterns, include
from django.contrib import admin

import testproject.testapp.urls

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^api/', include(testproject.testapp.urls)),
)
