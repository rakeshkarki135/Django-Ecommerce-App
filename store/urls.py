from django.urls import path 
from . import views 
from django.conf import settings 
from django.conf.urls.static import static
from .middlewares.auth import AuthMiddleware 

urlpatterns = [
     path('', views.Index.as_view() , name="index"),
     path('signup' , views.Signup.as_view(), name="signup"),
     path('login', views.Login.as_view(), name="login"),
     path('logout', views.logout, name="logout"),
     path('cart', views.Cart.as_view(), name="cart"),
     path('check-out' , views.Checkout.as_view() , name="check-out"),
     path('orders' , AuthMiddleware(views.OrderView.as_view()), name='orders'),
     path('forget-password', views.ForgotPassword.as_view(), name="forget-password"),
     path('change-password/<token>/', views.change_password, name="change-password"),
     
]


urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
     