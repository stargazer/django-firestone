from django.conf.urls import patterns, include
from django.contrib import admin
#import project.api.accounts.urls

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    #(r'^api/', include(project.api.accounts.urls)),
)
