from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from .yasg import urlpatterns as doc_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/account/', include('apps.account.urls')),
    path('api/education_plan/', include('apps.education_plan.urls')),
    path('api/schedule/', include('apps.schedule.urls')),
] + doc_urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
