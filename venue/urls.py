from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


from venues.urls import router

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/catering/', include('catering.urls')),
]

# Media faýllar üçin (DEBUG=True wagtynda)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
