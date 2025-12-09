from django import forms
from .models import Phone, Customer
class PhoneForm(forms.ModelForm):
    class Meta:
        model = Phone
        fields = ['brand','name','sku','price','storage','ram','color','stock','image','description']
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name','phone','email']
