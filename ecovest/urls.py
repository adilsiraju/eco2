from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('users/', include('users.urls')),
    path('initiatives/', include('initiatives.urls')),
    path('investments/', include('investments.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)