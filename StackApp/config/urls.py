from django.contrib import admin
from django.urls import path, include

import qanda.urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(qanda.urls, namespace='qanda')),
]
