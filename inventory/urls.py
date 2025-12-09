from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.phone_list, name='phone_list'),
    path('phones/add/', views.phone_create, name='phone_create'),
    path('phones/<int:pk>/', views.phone_detail, name='phone_detail'),
    path('phones/<int:pk>/edit/', views.phone_update, name='phone_update'),
    path('phones/<int:pk>/delete/', views.phone_delete, name='phone_delete'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('sell/', views.sell_phone, name='sell_phone'),
    path('reports/export-csv/', views.export_csv, name='export_csv'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Registration
    path('register/', views.register, name='register'),

    # Login & Logout using Django's built-in views
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),

    path('logout/', views.logout_user, name='logout'),

    path('shop/', views.shop, name='shop'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:phone_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:phone_id>/', views.remove_from_cart, name='remove_from_cart'),


]

