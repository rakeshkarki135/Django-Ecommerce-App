from django.shortcuts import render,HttpResponse,redirect,HttpResponseRedirect
from django.contrib.auth.hashers import make_password, check_password
from .models.product import Product
from .models.category import Category
from .models.customer import Customer
from .models.orders import Order
from .models.profile import Profile 
from django.utils.decorators import method_decorator
from .middlewares.auth import AuthMiddleware
from django.views import View
from .helper import send_forget_password
import uuid 


# Create your views here.
class Index(View):
     def get(self, request):
          # getting session
          cart = request.session.get('cart')
          if not cart:
               request.session['cart'] = {}
          products = None
          categories = Category.get_all_categories()
          categoryId = request.GET.get('category')
          if categoryId:
               products = Product.get_all_products_by_categoryId(categoryId)
          else:
               products = Product.get_all_products()
               
          context = {
               'products':products,
               'categories':categories
               
          }
          # print(request.session.get('customer_email'))
          return render(request, 'index.html', context)
     
     def post(self, request):
          # get product id
          product =  request.POST.get('product')
          # to remove form cart
          remove = request.POST.get('remove')
          # get cart from session
          cart = request.session.get('cart')
          if cart:
               quantity = cart.get(product)  
               if quantity:
                    if remove:
                         if quantity <= 1:
                              cart.pop(product)
                         else:
                              cart[product] = quantity - 1
                    else:
                         cart[product] = quantity + 1
               else:
                    cart[product] = 1
          else:
               cart = {}
               cart[product] = 1
          # storing data from cart to session
          request.session['cart'] = cart
          # print(request.session['cart'])
          return redirect("index")
          

class Signup(View):
     def get(self, request):
          return render(request,  'signup.html' )
     
     def post(self, request):
          postData = request.POST
          first_name = postData.get('firstname')
          last_name = postData.get('lastname')
          phone = postData.get('phone')
          email = postData.get('email')
          password = postData.get('password1')
          password2 = postData.get('password2')
          
          
          customer = Customer(
               first_name = first_name,
               last_name = last_name,
               phone = phone,
               email = email,
               password = password
                              
               )
          
          # validation
          value = {
               'first_name': first_name,
               'last_name': last_name,
               'phone' : phone,
               'email' : email,
               }
          error_message = self.validateCustomer(customer)
                    
          if not error_message:
               customer.password = make_password(customer.password)
               customer.register()
               
               profile = Profile.objects.create(user = customer)
               profile.save()
               
               return redirect("index")
          else:
               data = {
                    'error' : error_message,
                    'values' : value
               }
               return render(request, 'signup.html',data)
          
     def validateCustomer(self, customer):
          error_message = None
          if(not customer.first_name):
               error_message = "First Name required!!"
          elif len(customer.first_name) < 4:
               error_message = "First Name must be atleast 4 character"
          elif not customer.last_name:
               error_message = "Last Name is required!!"
          elif len(customer.last_name) < 4:
               error_message = "Last Name must be at least 4 characters"
          elif not customer.phone:
               error_message = "Phone is required"
          elif len(customer.phone) < 10:
               error_message = "Phone must be at least 10 characters"
          elif not customer.password:
               error_message = "Password is required!!"
          elif len(customer.password) < 6:
               error_message = "Password must be al least 6 characters"
          elif customer.is_Exists():
               error_message = "Email already Exists"
               
     
class Login(View):
     return_url = None
     def  get(self, request):
          Login.return_url = request.GET.get('return_url')
          return render(request, 'login.html')
     
     def post(self, request):
          email = request.POST.get('email')
          pswd = request.POST.get('password')
          
          customer = Customer.get_customer_by_email(email)
          error_message = None
          
          if customer:
               flag = check_password(pswd, customer.password )
               if flag:
                    # saving the user id 
                    request.session['customer'] = customer.id
                    
                    if Login.return_url:
                         return HttpResponseRedirect(Login.return_url)                        
                    else:
                         Login.return_url = None
                         return redirect("index")
               else:
                    error_message = "Incorrect password"
                    
          else:
               error_message = 'User does not Exist'
               
          return render(request, 'login.html', {'error':error_message })
          
          
def logout(request):
     request.session.clear()
     return redirect("login")

class Cart(View):
     def get(self, request):
          # getting the ids of the product
          ids = list(request.session.get('cart').keys())
          products = Product.get_products_by_id(ids)
          return render(request, 'cart.html', {'products':products})
     
class Checkout(View):
     def post(self, request):
          address = request.POST.get('address')
          phone = request.POST.get('phone')
          customer = request.session.get('customer')
          cart = request.session.get('cart')
          products = Product.get_products_by_id(list(cart.keys()))
          
          for product in products:
               order = Order(customer = Customer(id = customer),
                              product = product,
                              price = product.price,
                              address = address,
                              phone = phone,
                              quantity = cart.get(str(product.id))
               )
               order.place_order()
               # replace cart with empty session
               request.session['cart'] = {}
               
          return redirect('cart')
     

class OrderView(View):
     # @method_decorator(AuthMiddleware)
     def get(self, request):
          customer = request.session.get('customer')
          orders = Order.get_orders_by_customer(customer)
          # print(orders)
          return render(request, 'orders.html', {'orders':orders})
     
class ForgotPassword(View):
     def get(self, request):
          return render(request, 'forgetpassword.html')
     
     def post(self, request):
          context = {}
          email = request.POST.get('email')
          
          if Customer.objects.filter(email = email).exists():
               user_obj = Customer.objects.get(email = email)
               token = str(uuid.uuid4())
               profile_obj = Profile.objects.get(user = user_obj.id)
               profile_obj.forget_password_token = token
               profile_obj.save()
               send_forget_password(email, token)
               context['message'] = 'An Email is sent '
          else:
               context['message'] = 'User doesnot exist'
          
          return render(request, 'forgetpassword.html', context)
     
def change_password(request, token):
     context = {}
     
     try:
          profile_obj = Profile.objects.filter(forget_password_token = token).first()
          
          if request.method == 'POST':
               new_password = request.POST.get('new_password')
               confirm_password = request.POST.get('confirm_password')
               user_id = request.POST.get('user_id')
               
               
               if user_id is None:
                    context['message'] = 'User id is not Found'
                    return redirect(f'/change-password/{token}/')
                    
               if new_password != confirm_password:
                    context['message'] = 'Password doesnot Match'
                    print("paord doesnot match")
                    return redirect(f'/change-password/{token}/')
                    
               user_obj = Customer.objects.get(id = user_id)
               print(user_obj)
               user_obj.set_password(new_password)
               user_obj.save()
               print("passwword changed")
               return redirect('/login/')
          
               
     except Exception as e:
          pass 
     
     context = {'user_id' : profile_obj.user.id}
     return render(request, 'passwordreset.html', context)