from .models import *

# DRF
from rest_framework import serializers
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'title')

class MenuItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.title')
    class Meta:
        model = MenuItem
        fields = ('id', 'title', 'price', 'featured', 'category', 'category_name')
        
        
class CartSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='user.username')
    menuitem_name = serializers.CharField(source='menuitem.title')
    menuitem_price = serializers.DecimalField(source='menuitem.price', max_digits=6, decimal_places=2)
    total_price = serializers.SerializerMethodField('get_total_price')
    class Meta:
        model = Cart
        fields = ('id', 'customer_name', 'menuitem', 'menuitem_name', 'menuitem_price', 'quantity', 'unit_price', 'total_price')
        
    def get_total_price(self, obj):
        return obj.quantity * obj.unit_price
    
class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='user.username')
    delivery_crew_name = serializers.SerializerMethodField('get_delivery_crew_name')
    class Meta:
        model = Order
        fields = ('id', 'customer_name', 'delivery_crew', 'delivery_crew_name', 'status', 'total', 'date')
        
    def get_delivery_crew_name(self, obj):
        if obj.delivery_crew is None:
            return ''
        else:
            return obj.delivery_crew.username