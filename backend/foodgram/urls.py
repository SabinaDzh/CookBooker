from django.contrib import admin
from django.urls import include, path
from api.short_url import short_url_redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('<str:surl>/', short_url_redirect, name='short_url_redirect'),
]
