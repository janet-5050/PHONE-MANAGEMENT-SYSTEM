from django.db import models
from django.urls import reverse
class Brand(models.Model):
    name = models.CharField(max_length=120, unique=True)
    def __str__(self): return self.name
class Phone(models.Model):
    brand = models.ForeignKey(Brand,on_delete=models.PROTECT,related_name='phones')
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=80, unique=True)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    storage = models.CharField(max_length=50,blank=True)
    ram = models.CharField(max_length=50,blank=True)
    color = models.CharField(max_length=50,blank=True)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='phones/',blank=True,null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-created_at']
    def __str__(self): return f"{self.brand.name} {self.name}"
    def get_absolute_url(self): return reverse('inventory:phone_detail', args=[self.pk])
class Customer(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name
class Order(models.Model):
    customer = models.ForeignKey(Customer,null=True,blank=True,on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12,decimal_places=2,default=0)
    note = models.TextField(blank=True)
    def __str__(self): return f"Order #{self.pk} - {self.created_at.date()}"
class OrderItem(models.Model):
    order = models.ForeignKey(Order,related_name='items',on_delete=models.CASCADE)
    phone = models.ForeignKey(Phone,on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10,decimal_places=2)
    def line_total(self): return self.quantity * self.unit_price
    def __str__(self): return f"{self.phone} x {self.quantity}"
