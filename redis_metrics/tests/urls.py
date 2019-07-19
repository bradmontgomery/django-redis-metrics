from __future__ import unicode_literals
from django.urls import include, re_path
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^metrics/', include('redis_metrics.urls')),
]
