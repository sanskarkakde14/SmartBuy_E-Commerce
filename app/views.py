from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from .models import Customer, Product, Cart, OrderPlaced
from .forms import CustomerRegistrationForm, CustomerProfileForm
from django.views import View
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class ProductView(View):
    def get(self, request):
        totalitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        furniture = Product.objects.filter(category='FU')
        fashion = Product.objects.filter(category='F')
        toys = Product.objects.filter(category='TY')
        electronics = Product.objects.filter(category='E')
        homeappliance = Product.objects.filter(category='HA')
        return render(request, 'app/home.html',
                      {'furniture': furniture, 'fashion': fashion, 'electronics': electronics, 'toys': toys,
                       'homeappliance': homeappliance,'totalitem': totalitem})


class ProductDetailView(View):
    def get(self, request, pk):
        totalitem = 0
        product = Product.objects.get(pk=pk)
        item_already_in_cart = False
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            item_already_in_cart = Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
        return render(request, 'app/productdetail.html',
                      {'product': product, 'item_already_in_cart': item_already_in_cart, 'totalitem': totalitem})


@login_required()
def add_to_cart(request):
    user = request.user
    item_already_in_cart1 = False
    product = request.GET.get('prod_id')
    item_already_in_cart1 = Cart.objects.filter(Q(product=product) & Q(user=request.user)).exists()
    if not item_already_in_cart1:
        product_title = Product.objects.get(id=product)
        Cart(user=user, product=product_title).save()
        messages.success(request, 'Product Added to Cart Successfully !!')
        return redirect('/cart')
    else:
        return redirect('/cart')


@login_required
def show_cart(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0.0
        shipping_amount = 0
        totalamount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        print(cart_product)
        if cart_product:
            for p in cart_product:
                tempamount = (p.quantity * p.product.discounted_price)
                amount += tempamount
            totalamount = amount + shipping_amount
            return render(request, 'app/addtocart.html',
                          {'carts': cart, 'amount': amount, 'totalamount': totalamount, 'totalitem': totalitem})
        else:
            return render(request, 'app/emptycart.html', {'totalitem': totalitem})
    else:
        return render(request, 'app/emptycart.html', {'totalitem': totalitem})


def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity += 1
        c.save()
        amount = 0.0
        shipping_amount = 0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': amount + shipping_amount
        }
        return JsonResponse(data)
    else:
        return HttpResponse("")


def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity -= 1
        c.save()
        amount = 0.0
        shipping_amount = 0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': amount + shipping_amount
        }
        return JsonResponse(data)
    else:
        return HttpResponse("")


@login_required
def checkout(request):
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=request.user)
    amount = 0.0
    shipping_amount = 0
    totalamount = 0.0
    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    if cart_product:
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
        totalamount = amount + shipping_amount
    return render(request, 'app/checkout.html', {'add': add, 'cart_items': cart_items, 'totalcost': totalamount})


@login_required
def payment_done(request):
    custid = request.GET.get('custid')
    print("Customer ID", custid)
    user = request.user
    cartid = Cart.objects.filter(user=user)
    customer = Customer.objects.get(id=custid)
    print(customer)
    for cid in cartid:
        OrderPlaced(user=user, customer=customer, product=cid.product, quantity=cid.quantity).save()
        print("Order Saved")
        cid.delete()
        print("Cart Item Deleted")
    return redirect("orders")


def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        amount = 0.0
        shipping_amount = 0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
        data = {
            'amount': amount,
            'totalamount': amount + shipping_amount
        }
        return JsonResponse(data)
    else:
        return HttpResponse("")


@login_required
def address(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    add = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html', {'add': add, 'active': 'btn-primary', 'totalitem': totalitem})


@login_required
def orders(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    op = OrderPlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html', {'order_placed': op, 'totalitem': totalitem})


def electronic(request, data=None):
    totalitem = 0
    electronics = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    if data == None:
        electronics = Product.objects.filter(category='E')
    elif data == 'Apple' or data == 'Samsung' or data == 'LG' or data == 'Google':
        electronics = Product.objects.filter(category='E').filter(brand=data)
    elif data == 'below':
        electronics = Product.objects.filter(category='E').filter(discounted_price__lt=10000)
    elif data == 'above':
        electronics = Product.objects.filter(category='E').filter(discounted_price__gt=10000)
    return render(request, 'app/electronic.html', {'electronics': electronics, 'totalitem': totalitem})


def furnitures(request, data=None):
    totalitem = 0
    furniture = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    if data == None:
        furniture = Product.objects.filter(category='FU')
    elif data == 'IKEA' or data == 'PELLOS':
        furniture = Product.objects.filter(category='FU').filter(brand=data)
    elif data == 'below':
        furniture = Product.objects.filter(category='FU').filter(discounted_price__lt=10000)
    elif data == 'above':
        furniture = Product.objects.filter(category='FU').filter(discounted_price__gt=10000)
    return render(request, 'app/furniture.html', {'furniture': furniture, 'totalitem': totalitem})


def toys(request, data=None):
    totalitem = 0
    toy = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    if data == None:
        toy = Product.objects.filter(category='TY')
    elif data == 'LEGO' or data == 'WireScorts':
        toy = Product.objects.filter(category='TY').filter(brand=data)
    elif data == 'below':
        toy = Product.objects.filter(category='TY').filter(discounted_price__lt=10000)
    elif data == 'above':
        toy = Product.objects.filter(category='TY').filter(discounted_price__gt=10000)
    return render(request, 'app/toys.html', {'toy': toy, 'totalitem': totalitem})


def fashion(request, data=None):
    totalitem = 0
    cloth = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    if data == None:
        cloth = Product.objects.filter(category='F')
    elif data == 'Jockey' or data == 'Puma' or data == 'Van_Heusen' or data == 'Levi':
        cloth = Product.objects.filter(category='F').filter(brand=data)
    elif data == 'below':
        cloth = Product.objects.filter(category='F').filter(discounted_price__lt=10000)
    elif data == 'above':
        cloth = Product.objects.filter(category='F').filter(discounted_price__gt=10000)
    return render(request, 'app/fashion.html', {'cloth': cloth, 'totalitem': totalitem})


def appliance(request, data=None):
    totalitem = 0
    appliances = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    if data == None:
        appliances = Product.objects.filter(category='HA')
    elif data == 'Philips' or data == 'Samsung' or data == 'Prestige':
        appliances = Product.objects.filter(category='HA').filter(brand=data)
    elif data == 'below':
        appliances = Product.objects.filter(category='HA').filter(discounted_price__lt=10000)
    elif data == 'above':
        appliances = Product.objects.filter(category='HA').filter(discounted_price__gt=10000)
    return render(request, 'app/homeappliances.html', {'appliances': appliances, 'totalitem': totalitem})


def search(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    if request.method == 'POST':
        sea = request.POST['search']
        final = Product.objects.filter(description__icontains=sea) | Product.objects.filter(title__icontains=sea)
        return render(request, 'app/search.html',{'final':final,'sea':sea, 'totalitem': totalitem})
    else:
        return render(request, 'app/search.html')

class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html', {'form': form})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Congratulations!! Registered Successfully.')
            form.save()
        return render(request, 'app/customerregistration.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        totalitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        form = CustomerProfileForm()
        return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary', 'totalitem': totalitem})

    def post(self, request):
        totalitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            reg = Customer(user=usr, name=name, locality=locality, city=city, state=state, zipcode=zipcode)
            reg.save()
            messages.success(request, 'Congratulations!! Profile Updated Successfully.')
        return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary', 'totalitem': totalitem})


def contact(request):
    return render(request,'app/contact.html')

def thankyou(request):
    return render(request,'app/thankyou.html')

def aboutus(request):
    return render(request,'app/aboutus.html')





