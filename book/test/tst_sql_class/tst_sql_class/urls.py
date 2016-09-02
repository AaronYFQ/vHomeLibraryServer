from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'tst_sql_class.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^book/', include('app.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
