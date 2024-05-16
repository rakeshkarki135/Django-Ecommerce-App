from django.db import models 
from .customer import Customer  
from datetime import datetime 

class Profile(models.Model):
     user = models.OneToOneField(Customer, on_delete=models.CASCADE)
     forget_password_token = models.CharField(max_length=100)
     created_at = models.DateTimeField(auto_now_add=True)
     
     def __str__(self):
          return self.user.first_name