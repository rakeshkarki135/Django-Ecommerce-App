from django.contrib import admin
from .models.product import Product
from .models.category import Category
from .models.customer import Customer 
from .models.orders import Order 
from .models.profile import Profile

# Register your models here.
class AdminProduct(admin.ModelAdmin):
     list_display = ['name','price','category']
admin.site.register(Product,AdminProduct)

class CategoryAdmin(admin.ModelAdmin):
     list_display = ['name']
admin.site.register(Category,CategoryAdmin)

admin.site.register(Customer)

admin.site.register(Order)

admin.site.register(Profile)