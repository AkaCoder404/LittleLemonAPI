from django.contrib import admin
from .models import Category, MenuItem

# Register your models here.
admin.site.register(Category)


class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'featured', 'category')
    
    
admin.site.register(MenuItem, MenuItemAdmin)