from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from . models import *
from shopping.form import CustomUserForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
import  json
# Create your views here.
def home(request):
    products=Product.objects.filter(trending=1)
    return render(request,"shopping/index.html",{"products":products})
def cart_page(request):
    if request.user.is_authenticated:
        cart=Cart.objects.filter(user=request.user)
        return render(request,"shopping/cart.html",{"cart":cart})

    else:
        return redirect("/")
def favviewpage(request):
    if request.user.is_authenticated:
        fav=Favourite.objects.filter(user=request.user)
        return render(request,"shopping/fav.html",{"fav":fav})

    else:
        return redirect("/")
def remove_fav(request,id):
    item=Favourite.objects.get(id=id)
    item.delete()
    return redirect('/favviewpage')
def remove_cart(request,id):
    cartitem=Cart.objects.get(id=id)
    cartitem.delete()
    return redirect('/cart')
def fav_page(request):
    if request.headers.get('x-requested-with')=='XMLHttpRequest':
        if request.user.is_authenticated:
            
        
            data=json.load(request)
            
            Product_id=data['pid']
            product_status=Product.objects.get(id=Product_id)
            if product_status:

                if Favourite.objects.filter(user=request.user.id,Product_id=Product_id):
                    return JsonResponse({'status':'Product Already in  Favourite'}, status=200)
                else:
                    Favourite.objects.create(user=request.user,Product_id=Product_id)
                    return JsonResponse({'status':'Product Added to Favourite'}, status=200)
            else:
                return JsonResponse({'status': 'Product does not exist'}, status=200)


        else:
            return JsonResponse({'status':'Login to Add Favourite'}, status=200)
    else:
        return JsonResponse({'status':'Invalid Access'}, status=200)

def add_to_cart(request):
    if request.headers.get('x-requested-with')=='XMLHttpRequest':
        if request.user.is_authenticated:
            try:
        
                data=json.load(request)
                Product_qty=data['Product_qty']
                Product_id=data['pid']
                #print(request.user.id)
                product_status=Product.objects.get(id=Product_id)
                if product_status:
                    if Cart.objects.filter(user=request.user.id,Product_id=Product_id):
                        return JsonResponse({'status':'Product Already in Cart'}, status=200)
                    else:
                        if product_status.quantity>=Product_qty:
                            Cart.objects.create(user=request.user,Product_id=Product_id,product_qty=Product_qty)
                            return JsonResponse({'status':'Product Added to Cart'}, status=200)
                        else:
                            return JsonResponse({'status':'Product Stock Not Available'}, status=200)
                else:
                    return JsonResponse({'status': 'Incomplete or Invalid Data'}, status=200)
                
            except json.JSONDecodeError:
                print("Invalid JSON Data:", request.body)
                return JsonResponse({'status': 'Invalid JSON Data'}, status=400)
        else:
            return JsonResponse({'status':'Login to Add Cart'}, status=200)
    else:
        return JsonResponse({'status':'Invalid Access'}, status=200)





def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,"Logged out Successfully")
    return redirect("/")

def login_page(request):
    if request.user.is_authenticated:
        return redirect("/")

    else:
        if request.method=='POST':
            name=request.POST.get('username')
            pwd=request.POST.get('password')
            user=authenticate(request,username=name,password=pwd)
            if user is not None:
                login(request,user)
                messages.success(request,"Logged in Successfully")
                return redirect("/")
            else:
                messages.error(request,"Invalid User Name or Password")
                return redirect("/login")
        return render(request,"shopping/login.html")

def register(request):
    form=CustomUserForm()
    if request.method=='POST':
        form=CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Registration Success You can login now")
            return redirect('/login')
    return render(request,"shopping/register.html",{'form':form})

def collections(request):
    category=Category.objects.filter(status=0)
    return render(request,"shopping/collection.html",{"category":category})

def collectionsview(request,name):
    if(Category.objects.filter(name=name,status=0)):
        products=Product.objects.filter(category__name=name)
        return render(request,"shopping/products/index.html",{"products":products,"category_name":name})
    else:
        messages.warning(request,"No suck category found")
        return redirect('collections')
    
def product_details(request,cname,pname):
    if(Category.objects.filter(name=cname,status=0)):
        if(Product.objects.filter(name=pname,status=0)):
            products=Product.objects.filter(name=pname,status=0).first()
            return render(request,"shopping/products/product_details.html",{"products":products})
        else:
            messages.error(request,"No such product found")
            return redirect('collections')
    else:
        messages.warning(request,"No suck category found")
        return redirect('collections')

