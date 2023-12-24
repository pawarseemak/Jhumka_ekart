from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from ecomm_app.models import Product, Cart, Order, Query
from django.db.models import Q
import random
import razorpay
from django.core.mail import send_mail

# Create your views here.
def home(request):
    #userid=request.user.id
    #print("id of logged user", userid)
    #print("result:", request.user.is_authenticated)
    p=Product.objects.filter(is_active=True)
    #print(p) #list of 5 objects
    context={}
    context['products']=p
    return render(request,'index.html', context)

def product_details(request, pid):
    p=Product.objects.filter(id=pid)
    #print(p)
    context={}
    context['products']=p
    return render(request, 'product_details.html', context)

def register(request):
    if request.method=='POST':
        uname=request.POST['uname']
        upass=request.POST['upass']
        ucpass=request.POST['ucpass']
        context={}
        #print(uname,"-", upass,"-",ucpass)
        if uname=="" or upass=="" or ucpass=="":
            context['errmsg']="!-----Fields cannot be blank-----!"
            return render(request,'register.html', context)
        elif upass != ucpass:
            context['errmsg']="!------Mismatch in Password & Confirm Password------!"
            return render(request,'register.html',context)
        else:
            try:
                u=User.objects.create(password=upass, username=uname, email=uname)
                u.set_password(upass)
                u.save()
                context['success']="User Created Successfully. Please Login..!"
                return render(request, 'register.html', context)
                #return HttpResponse("User created successfully")
            except Exception:
                context['errmsg']="***---Username already exits......!"
                return render(request, 'register.html', context)
    else:
        return render(request,'register.html')

def user_login(request):
    if request.method=="POST":
        uname=request.POST['uname']
        upass=request.POST['upass']
        #print(uname, "--", upass)
        #return HttpResponse("data fetched success")
        context={}
        if uname=="" or upass=="":
            context['errmsg']="Fields cannot be empty"
            return render(request, 'login.html', context)
        else:
            u=authenticate(username=uname, password=upass)
            #print(u)
            if u is not None:
                login(request,u)
                return redirect('/home')
            else:
                context['errmsg']="Invalid username and password"
                return render(request, 'login.html',context)
            #print(u.username)
            #print(u.is_superuser)
            #return HttpResponse("in esle part")
    else:
        return render(request,'login.html')

def user_logout(request):
    logout(request)
    return redirect('/home')

def catfilter(request, cv):
    #print(cv)
    q1=Q(is_active=True)
    q2=Q(cat=cv)
    p=Product.objects.filter(q1 & q2)
    #print(p)
    context={}
    context['products']=p
    #return HttpResponse(cv)
    return render(request, 'index.html', context)

def sort(request,sv):
    if sv=="0":
        col='price'
    else:
        col="-price"
    p=Product.objects.filter(is_active=True).order_by(col)
    context={}
    context['products']=p
    return render(request, 'index.html', context)    


def range(request):
    min=request.GET['min']
    max=request.GET['max']
    #print(min)
    #print(max)
    q1=Q(price__gte=min)
    q2=Q(price__lte=max)
    q3=Q(is_active=True)
    p=Product.objects.filter(q1 & q2 & q3)
    context={}
    context['products']=p
    return render(request, 'index.html', context)
    #return HttpResponse("pass")

def addtocart(request, pid):
    if request.user.is_authenticated:
        userid=request.user.id
        #print(userid)
        #print(pid)
        u=User.objects.filter(id=userid)
        #print(u[0])
        p=Product.objects.filter(id=pid)
        #print(p[0])
        q1=Q(uid=u[0])
        q2=Q(pid=p[0])
        c=Cart.objects.filter(q1 & q2)
        n=len(c)
        context={}
        context['products']=p
        if n==1:
            context['msg']="Ahhh...Product already exits in cart!!"
        else:
            c=Cart.objects.create(uid=u[0], pid=p[0])
            c.save()
            context['success']="Product added successfully in cart..!!"
        return render(request,'product_details.html', context)
        #return HttpResponse("add to cart")
    else:
        return redirect('/login')

def viewcart(request):
    c=Cart.objects.filter(uid=request.user.id)
    #print(c)
    #print(c[0].uid)
    #print(c[0].pid)
    s=0
    np=len(c)
    #print(np)---lenghth of products in cart
    for x in c:
        #print(x)
        #print(x.pid.price)
        s=s+ x.pid.price*x.qty
    #print(s)
    context={}
    context['data']=c
    context['total']=s
    context['n']=np
    return render(request,'cart.html', context)

def remove(request, cid):
    c=Cart.objects.filter(id=cid)
    c.delete()
    return redirect('/viewcart')

def removefromplaceorder(request, pid):
    d=Order.objects.filter(id=pid)
    d.delete()
    return redirect('/placeorder')

def updateqty(request,qv,cid):
    c=Cart.objects.filter(id=cid)
    #print(c)
    #print(c[0].qty)
    if qv=="1":
        t=c[0].qty + 1
        c.update(qty=t)
    else:
        if c[0].qty>1:
            t=c[0].qty - 1
            c.update(qty=t)
    return redirect('/viewcart')
    #return HttpResponse("quantity")

def placeorder(request):
    userid=request.user.id
    c=Cart.objects.filter(uid=userid)
    #print(c)
    oid=random.randrange(1000,9999)
    #print(oid)
    for x in c:
        #print(x)
        #print(x.pid)
        #print(x.uid)
        #print(x.qty)
        o=Order.objects.create(order_id=oid,pid=x.pid,uid=x.uid,qty=x.qty)
        o.save()
        x.delete()
    orders=Order.objects.filter(uid=request.user.id)
    context={}
    context['data']=orders
    s=0
    np=len(orders)
    for x in orders:
        s=s+x.pid.price*x.qty
    context['total']=s
    context['n']=np
    #return HttpResponse("placeorder")
    return render(request,'placeorder.html', context)

def makepayment(request):
    uemail=request.user.username
    #print(uemail)
    orders=Order.objects.filter(uid=request.user.id)
    s=0
    np=len(orders)
    for x in orders:
        s=s + x.pid.price*x.qty
        oid=x.order_id
    client = razorpay.Client(auth=("rzp_test_1qq2AA77jN79S3", "96ImRkPDbjHuQPXXYMBCLFPn"))
    data = { "amount": s*100, "currency": "INR", "receipt": oid }
    payment = client.order.create(data=data)
    #print(payment)
    context={}
    context['data']=payment
    context['uemail']=uemail
     #return HttpResponse("success")
    return render(request, 'pay.html', context)

def sendusermail(request, uemail):
   # print("----",uemail)
    msg="Thank you for shopping with us"
    send_mail(
    "OnlineJhumka - You order has been placed successfully",
    msg,
    "seemakpawar14@gmail.com",
    [uemail],
    fail_silently=False,
)
    #return HttpResponse("success sent")
    return render(request, 'thankyou.html')


def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def create(request):
    if request.method=='POST':
        n=request.POST['uname']
        mobile=request.POST['umob']
        query=request.POST['uquery']
        #print(n, "--", mobile, "---", query)
        s=Query.objects.create(name=n,mobile=mobile,query=query)
        s.save()
        context={}
        context['success']="We value your time and will get back to you soon!!!!!"
        return render(request,'contact.html', context)

    else:
        return render(request,'contact.html')