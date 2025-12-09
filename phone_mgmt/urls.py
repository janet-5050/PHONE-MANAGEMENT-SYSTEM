from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Use your custom login template
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(template_name='registration/login.html'),
        name='login'
    ),

    # Custom logout – GET allowed (prevents 405 error)
    path(
        'accounts/logout/',
        auth_views.LogoutView.as_view(next_page='inventory:phone_list'),
        name='logout'
    ),

    # Your inventory app
    path('', include('inventory.urls', namespace='inventory')),
]

# Static and media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
