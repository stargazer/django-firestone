from django.conf.urls import patterns, include
from django.contrib import admin

import test_project.app.urls

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^api/', include(test_project.app.urls)),
)
