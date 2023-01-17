"""kcp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import path, include, re_path
from django.views.decorators.csrf import csrf_exempt

from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from stores import views

urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + [
    path('login/', include('shopify_auth.urls')),
    path('product/', views.ProductView.as_view()),
    path('product/update/', views.UpdateCustomPriceProductAPIView.as_view()),
    path('product/delete/', views.DeleteProductMetafield.as_view()),
    path('stores/webhooks/orders/', csrf_exempt(views.OrderWebhook.as_view())),
    path('admin/', admin.site.urls),
    re_path(r'^.*$', views.HomeView.as_view())
]
if settings.DEBUG:
    # Static file serving when using Gunicorn + Uvicorn for local web socket development
    urlpatterns = staticfiles_urlpatterns() + urlpatterns
