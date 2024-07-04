from django.contrib import admin
from django.urls import path, include
from myapp import urls
from .settings import STATIC_ROOT
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include('myapp.urls'))
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
urlpatterns += staticfiles_urlpatterns()