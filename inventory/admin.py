from django.contrib import admin
from .models import Brand, Phone, Customer, Order, OrderItem
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display=('name',)
@admin.register(Phone)
class PhoneAdmin(admin.ModelAdmin):
    list_display=('sku','name','brand','price','stock')
    list_filter=('brand',)
    search_fields=('name','sku')
    list_editable=('price','stock')
class OrderItemInline(admin.TabularInline):
    model=OrderItem; extra=0
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display=('id','created_at','customer','total'); inlines=[OrderItemInline]
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display=('name','phone','email')
