from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import *
import json
import datetime
# Create your views here.


def store(request):
     if request.user.is_authenticated:
          customer = request.user.customer
          order, created = Order.objects.get_or_create(customer=customer, complete=False)
          items = order.orderitem_set.all()
          cartItems = order.get_cart_items
     else:
          order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}  
          items = []  
          cartItems = order['get_cart_items']

     products = Product.objects.all()
     context = {'products': products,'cartItems':cartItems }
     return render(request, 'store.html', context)


def cart(request):
     print(request.user)
     if request.user.is_authenticated:
          print(request.user)
          customer = request.user.customer
          print(customer)
          order,create = Order.objects.get_or_create(customer=customer,complete=False)
          items = order.orderitem_set.all()
          cartItems = order.get_cart_items
     else:
         try:
            cart = json.loads(request.COOKIES['cart'])
         except:
              cart={}   
              print('CART:', cart)
         items = [] 
         order = {'get_cart_total':0, 'get_cart_items':0,'shipping':False} 
         cartItems = order['get_cart_items']  

         for i in cart:
               cartItems += cart[i]['quantity'] 

               products = Product.objects.get(id=i)
               total = (products.price * cart [i]['quantity'])

               order['get_cart_total'] += total
               order['get_cart_items'] += cart [i]['quantity']

               item ={
                    'product':{
                         'id':products.id,
                         'name':products.name,
                         'price':products.price,
                         'imageURL':products.imageURL
                    },
                    'quantity':cart [i]['quantity'],
                    'get_total':total,

               }
               items.append(item)
     context = {
          'items': items,
          'order':order,
          'cartItems':cartItems
     }
     return render(request, 'cart.html',context)

def checkout(request):
     if request.user.is_authenticated:
          customer = request.user.customer
          order, created = Order.objects.get_or_create(customer=customer, complete=False)
          items = order.orderitem_set.all()
          cartItems = order.get_cart_items
     else:
          order = {'get_cart_total':0, 'get_cart_items':0,'shipping':False}
          cartItems = order['get_cart_items']  
          items = [] 
           
     context = {'items': items, 'order':order,'cartItems':cartItems}
     return render(request, 'checkout.html', context)

def updateItem(request):
     data = json.loads(request.body)
     productId = data['productId']
     action = data['action']
       
     print('action:', action)
     print('poductId:', productId)

     customer = request.user.customer
     product = Product.objects.get(id=productId)
     order, created = Order.objects.get_or_create(customer=customer, complete=False)
     orderitem, created = OrderItem.objects.get_or_create(order=order, product=product)

     if action == 'add':
          orderitem.quantity = (orderitem.quantity +1)
     elif action == 'remove':
          orderitem.quantity = (orderitem.quantity -1)

     orderitem.save()

     if orderitem.quantity <= 0:
          orderitem.delete()
     return JsonResponse('item was added', safe=False)


def processOrder(request):
      transacton_Id = datetime.datetime.now().timestamp()
      data = json.loads(request.body)

      if request.user.is_authenticated:
           customer = request.user.customer
           order, created = Order.objects.get_or_create(customer=customer, complete=False)
           total = float(data['form']['total'])
           order.transacton_Id= transacton_Id

           if total == order.get_cart_total:
                order.complete = True
           order.save()

           if order.shipping == True:
                ShippingAddress.objects.create(
                     customer=customer,
                     order=order,
                     address=data['shipping']['address'],
                     city=data['shipping']['city'],
                     state=data['shipping']['state'],
                     zipcode=data['shipping']['zipcode']
                )     

      else:
           print('User is not logged in....')     
      return JsonResponse('payment complete!', safe=False)



# def login(request):
#      if request.method == 'POST':
#          username = request.POST['username']
#          password = request.POST['password']

#          User = auth.authenticate(username=username,password=password)
#          if User is not None:
#              auth.login(request, User)
#              return render(request, 'cart.html')
#          else:
#              messages.info(request, 'invalid credential') 
#              return redirect('login')   
#      else:
#         return render(request, 'login.html')        
   
# def signup(request):
#       if request.method == 'POST':
#         firstname = request.POST['firstname']
#         lastname = request.POST['lastname']
#         email = request.POST['email']
#         username = request.POST['username']
#         password1 = request.POST['password1']
#         password2 = request.POST['password2']
#         if password1==password2:
#             if User.objects.filter(username=username).exists():
#                 messages.info(request, 'username taken')
#                 return redirect('signup')
#             elif User.objects.filter(email=email).exists():
#                 messages.info(request, 'email taken')
#                 return redirect('signup')
#             else:        
#                users = User.objects.create_user(username=username, password=password1, email=email, first_name=firstname, last_name=lastname)
#                users.save()
#                print('user created')
#                return redirect('login')
#         else:
#             print('password is not matching....')
#             return redirect('signup')
#         return redirect('/')

#       else:    
#         return render(request, 'signup.html')