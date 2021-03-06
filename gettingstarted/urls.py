from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

import hello.views
import hello.service

# Examples:
# url(r'^$', 'gettingstarted.views.home', name='home'),
# url(r'^blog/', include('blog.urls')),

urlpatterns = [
    url(r'^$', hello.views.index, name='index'),
    url(r'^db', hello.views.db, name='db'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^recipes$', hello.views.search),
    url(r'^recipe/(.*)$', hello.views.recipe),
    url(r'^v2/recipes$', hello.service.search),
]
