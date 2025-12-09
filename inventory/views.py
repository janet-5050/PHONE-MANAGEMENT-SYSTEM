from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.http import HttpResponse
import csv
from .models import Phone, Brand, Order, OrderItem, Customer
from .forms import PhoneForm, CustomerForm
from django.contrib.auth.forms import UserCreationForm
def phone_list(request):
    q=request.GET.get('q',''); brand=request.GET.get('brand','')
    phones=Phone.objects.select_related('brand').all()
    if q:
        phones=phones.filter(name__icontains=q) | phones.filter(sku__icontains=q)
    if brand:
        phones=phones.filter(brand__name__iexact=brand)
    paginator=Paginator(phones,12); page=request.GET.get('page'); phones_page=paginator.get_page(page)
    brands=Brand.objects.all()
    return render(request,'inventory/phone_list.html',{'phones':phones_page,'brands':brands,'q':q,'brand_selected':brand})
def phone_detail(request, pk):
    phone=get_object_or_404(Phone,pk=pk)
    return render(request,'inventory/phone_detail.html',{'phone':phone})
@login_required
def phone_create(request):
    if request.method=='POST':
        form=PhoneForm(request.POST,request.FILES)
        if form.is_valid():
            form.save(); messages.success(request,'Phone added.'); return redirect('inventory:phone_list')
    else:
        form=PhoneForm()
    return render(request,'inventory/phone_form.html',{'form':form,'action':'Add'})
@login_required
def phone_update(request, pk):
    phone=get_object_or_404(Phone,pk=pk)
    if request.method=='POST':
        form=PhoneForm(request.POST,request.FILES,instance=phone)
        if form.is_valid():
            form.save(); messages.success(request,'Phone updated.'); return redirect('inventory:phone_detail',pk=phone.pk)
    else:
        form=PhoneForm(instance=phone)
    return render(request,'inventory/phone_form.html',{'form':form,'action':'Edit'})
@login_required
def phone_delete(request, pk):
    phone=get_object_or_404(Phone,pk=pk)
    if request.method=='POST':
        phone.delete(); messages.success(request,'Phone deleted.'); return redirect('inventory:phone_list')
    return render(request,'inventory/phone_confirm_delete.html',{'phone':phone})
@login_required
def dashboard(request):
    total=Phone.objects.count(); low=Phone.objects.filter(stock__lte=5).count()
    recent=Phone.objects.order_by('-created_at')[:6]
    return render(request,'inventory/dashboard.html',{'total_phones':total,'low_stock':low,'recent':recent})
@transaction.atomic
@login_required
def sell_phone(request):
    if request.method=='POST':
        cform=CustomerForm(request.POST)
        items=[]
        for k,v in request.POST.items():
            if k.startswith('phone_') and v:
                idx=k.split('_',1)[1]; qty=int(request.POST.get(f'qty_{idx}',1))
                items.append((int(v),qty))
        if not items:
            messages.error(request,'No items selected.'); return redirect('inventory:sell_phone')
        if cform.is_valid():
            customer=cform.save(); order=Order.objects.create(customer=customer); total=0
            for pid,qty in items:
                phone=Phone.objects.select_for_update().get(pk=pid)
                if phone.stock<qty:
                    transaction.set_rollback(True); messages.error(request,f'Not enough stock for {phone}.'); return redirect('inventory:sell_phone')
                OrderItem.objects.create(order=order,phone=phone,quantity=qty,unit_price=phone.price)
                phone.stock-=qty; phone.save(); total+=phone.price*qty
            order.total=total; order.save(); messages.success(request,'Sale recorded.'); return redirect('inventory:dashboard')
        else:
            messages.error(request,'Invalid customer data.'); return redirect('inventory:sell_phone')
    else:
        phones=Phone.objects.filter(stock__gt=0); customer_form=CustomerForm()
        return render(request,'inventory/sell.html',{'phones':phones,'customer_form':customer_form})
@login_required
def export_csv(request):
    response=HttpResponse(content_type='text/csv'); response['Content-Disposition']='attachment; filename=phones.csv'
    writer=csv.writer(response); writer.writerow(['SKU','Brand','Name','Price','Storage','RAM','Color','Stock'])
    for p in Phone.objects.select_related('brand').all():
        writer.writerow([p.sku,p.brand.name,p.name,str(p.price),p.storage,p.ram,p.color,p.stock])
    return response
def is_super(user): return user.is_active and user.is_superuser
@user_passes_test(is_super)
def admin_dashboard(request):
    total=Phone.objects.count(); total_brands=Brand.objects.count(); orders=Order.objects.count()
    return render(request,'inventory/admin_dashboard.html',{'total':total,'brands':total_brands,'orders':orders})
def register(request):
    if request.method=='POST':
        form=UserCreationForm(request.POST)
        if form.is_valid():
            user=form.save(); login(request,user); messages.success(request,'Welcome!'); return redirect('inventory:phone_list')
    else:
        form=UserCreationForm()
    return render(request,'inventory/registration.html',{'form':form})
def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('inventory:phone_list')
def shop(request):
    q = request.GET.get('q','')
    brand = request.GET.get('brand','')
    phones = Phone.objects.select_related('brand').all()

    if q:
        phones = phones.filter(name__icontains=q) | phones.filter(sku__icontains=q)
    if brand:
        phones = phones.filter(brand__name__iexact=brand)

    paginator = Paginator(phones, 12)
    page = request.GET.get('page')
    phones_page = paginator.get_page(page)

    brands = Brand.objects.all()

    return render(request, 'inventory/shop.html', {
        'phones': phones_page,
        'brands': brands,
        'q': q,
        'brand_selected': brand
    })
# Add phone to cart
def add_to_cart(request, phone_id):
    cart = request.session.get('cart', {})
    cart[phone_id] = cart.get(phone_id, 0) + 1  # increase quantity by 1
    request.session['cart'] = cart
    return redirect('inventory:shop')

# Remove phone from cart
def remove_from_cart(request, phone_id):
    cart = request.session.get('cart', {})
    if phone_id in cart:
        del cart[phone_id]
    request.session['cart'] = cart
    return redirect('inventory:cart')

# View cart
def cart(request):
    cart = request.session.get('cart', {})
    phone_ids = cart.keys()
    phones = Phone.objects.filter(id__in=phone_ids)
    cart_items = []
    total = 0
    for phone in phones:
        qty = cart[str(phone.id)]
        subtotal = phone.price * qty
        cart_items.append({'phone': phone, 'qty': qty, 'subtotal': subtotal})
        total += subtotal
    return render(request, 'inventory/cart.html', {'cart_items': cart_items, 'total': total})
def view_cart(request):
    # This is where you'd normally pass cart items from session or database
    cart = request.session.get('cart', {})
    return render(request, 'inventory/cart.html', {'cart': cart})

