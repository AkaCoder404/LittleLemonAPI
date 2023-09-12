from django.shortcuts import render
from django.core import serializers
from django.db.models import F
import json
import datetime

# Models
from .models import *
from .serializers import *
from django.contrib.auth.models import User, Group

# DRF Imports
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator 



# User roles


# Create your views here.
# Category Endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def categories(request):
    all_categories = Category.objects.all()
    all_categories = CategorySerializer(all_categories, many=True).data
    return Response(all_categories, status=status.HTTP_200_OK)
    

# Menu Items Endpoints
@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def menu_items(request):
    """ Menu-items endpoints """
    # Check if user is Manager, Customer, or Delivery Crew
    
    # Handle Manager actions
    isManager = request.user.groups.filter(name='Manager').exists()
    if isManager:
        print("Manager Request")
        if request.method == 'GET':
            # Get all menu items
            all_menu_items = get_all_menu_items()
            return Response(all_menu_items, status=status.HTTP_200_OK)
        elif request.method == 'POST':
            # Create new menu item
            data = request.data
            title = data['title']
            price = data['price']
            featured = data['featured']
            category = data['category']

            # First check if category exists
            categoryExists = Category.objects.filter(title=category).exists()
            if categoryExists is False:
                # Create new category
                category = Category.objects.create(title=category)
                category.save()
            else:
                # Get category
                category = Category.objects.get(title=category)
                
            # Create new menu item
            new_item = MenuItem.objects.create(title=title, price=price, featured=featured, category=category)
            new_item.save()
            return Response(status=status.HTTP_201_CREATED)
            
    # Handle Customer/Delivery Crew actions
    if request.method != 'GET':
        print("Customer/Delivery Crew Request Unauthorized")
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    # 
    if request.method == 'GET':
        all_menu_items = get_all_menu_items()
        return Response(all_menu_items, status=status.HTTP_200_OK)
  
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def menu_items_pag(request):
     
    page = request.GET.get('page')
    orderby_param = request.GET.get('orderby')
    category = request.GET.get('category')
    
    ordering = []
    if orderby_param:
        orderby_values = orderby_param.split(',')
        for value in orderby_values:
            if value.startswith('-'):
                ordering.append(F(value[1:]).desc())
            else:
                ordering.append(value)
                
   
    menu_items = MenuItem.objects.filter(category=category).order_by(*ordering or default_ordering)
    count = len(menu_items)
    
    paginator = Paginator(menu_items, 2)
    
    try:
        page = paginator.page(page)
    except:
        # Page is out of range
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    # Check if there is next page
    try: 
        # print("Next", page.has_next(), page.next_page_number())
        next = "http://127.0.0.1:8000/api/menu-items-page/?page=" + str(page.next_page_number())
    except: 
        next = ""
    # Check if there is previous page
    try:
        # print("Previous", page.has_previous(), page.previous_page_number())
        previous = "http://127.0.0.1:8000/api/menu-items-page/?page=" + str(page.previous_page_number())
    except:
        previous = ""
    
    menu_items = page.object_list
    menu_items = MenuItemSerializer(menu_items, many=True).data
    result = {
        'count': count,
        'next': next,
        'previous': previous,
        'results': menu_items
    }
    return Response(result, status=status.HTTP_200_OK)
     
    
@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def menu_item(request, menuItem):
    if request.method == 'GET':
        # Get menu item
        try:
            menu_item = MenuItem.objects.get(id=menuItem)
            menu_item = MenuItemSerializer(menu_item).data
            return Response(menu_item, status=status.HTTP_200_OK)
        except Exception as e:
            message = {"message": "Menu item not found"}
            return Response(message, status=status.HTTP_404_NOT_FOUND)
    
    # If Not Mangager, return 403 Forbidden for all other methods 
    isManager = request.user.groups.filter(name='Manager').exists()
    if isManager is False:
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    # Handle Manager actions
    if request.method in ['PUT', 'PATCH']:
        # Update menu item
        data = request.data
        menu_item = MenuItem.objects.get(id=menuItem)
        menu_item.title = data['title']
        menu_item.price = data['price']
        menu_item.featured = data['featured']
        
        # First check if category exists
        categoryExists = Category.objects.filter(title=data['category']).exists()
        if categoryExists:
            # Get category
            category = Category.objects.get(title=data['category'])
            menu_item.category = category
        else:
            # Create new category
            category = Category.objects.create(title=data['category'])
            category.save()
            menu_item.category = category
        
        menu_item.save()
        return Response(status=status.HTTP_200_OK)
    
    if request.method == 'DELETE':
        # Delete menu item
        menu_item = MenuItem.objects.get(id=menuItem)
        menu_item.delete()
        return Response(status=status.HTTP_200_OK)
    
    
# Group management endpoints
@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def groups_manager_users(request):
    """ User groups management endpoints """
    isManager = request.user.groups.filter(name='Manager').exists()
    if isManager:
        if request.method == 'GET':
            # Return all managers
            managers = User.objects.filter(groups__name='Manager').values("id", "username", "email")
            result = {
                "managers": [manager for manager in managers]
            }
            return Response(result, status=status.HTTP_200_OK)
        
        if request.method == 'POST':
            # Assigns the user in the payload to the manager group
            payload = request.data
            user = User.objects.get(id=payload['user_id'])
            # Add user to "Manager" group
            manager_group = Group.objects.get(name='Manager')
            manager_group.user_set.add(user)
            return Response(status=status.HTTP_201_CREATED)
            
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)
    
@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def groups_delivery_crew_users(request):
    """ User groups management endpoints """
    isManager = request.user.groups.filter(name='Manager').exists()
    if isManager:
        if request.method == 'GET':
            # Return all delivery crew
            delivery_crew = User.objects.filter(groups__name='Delivery Crew').values("id", "username", "email")
            result = {
                "delivery_crew": [crew for crew in delivery_crew]
            }
            return Response(result, status=status.HTTP_200_OK)
            
        if request.method == 'POST':
            # Assigns the user in the payload to the delivery crew group
            payload = request.data
            user = User.objects.get(id=payload['user_id'])
            # Add user to "Manager" group
            manager_group = Group.objects.get(name='Manager')
            manager_group.user_set.add(user)
            return Response(status=status.HTTP_201_CREATED)               
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)

# @api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
# def groups_managers_users(request, userId):
#     """ remove user from manager group """

@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def make_delivery_crew(request):
    isManager = request.user.groups.filter(name='Manager').exists()
    if isManager == False:
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    user = User.objects.get(id=request.data['user_id'])
    delivery_crew_group = Group.objects.get(name='Delivery Crew')
    if request.method == "POST":
        # Make user delivery crew
        delivery_crew_group.user_set.add(user)
        return Response(status=status.HTTP_201_CREATED)

    if request.method == "DELETE":
        # REmove user from delivery crew
        delivery_crew_group.user_set.remove(user)
        return Response(status=status.HTTP_200_OK)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_manager(request, userId):
    """ remove user from manager group """
    isManager = request.user.groups.filter(name='Manager').exists()
    if isManager:
        try: 
            # Check if user exists
            user = User.objects.get(id=userId)
        except Exception as e:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        # Check if user is in managers
        managers = User.objects.filter(groups__name='Manager')
        isManager = managers.filter(id=userId).exists()
        if isManager == False: # if user is not manager
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        # In manager, remove
        user = User.objects.get(id=userId)
        manager_group = Group.objects.get(name='Manager')
        manager_group.user_set.remove(user)
        return Response(status=status.HTTP_200_OK)
        
# Cart management endpoints
@api_view(['GET','POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart(request):
    # Check if user is Customer
    isManager = request.user.groups.filter(name='Manager').exists()
    isDelivery = request.user.groups.filter(name='Delivery Crew').exists()
    if isManager == True or isDelivery == True:
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        # Get all cart items
        cart_items = Cart.objects.filter(user=request.user)
        cart_items = CartSerializer(cart_items, many=True).data
        count = len(cart_items)
        results = [item for item in cart_items]
        payload = {
            'count': count,
            'cart_total': sum([item['total_price'] for item in cart_items]),
            'results': results
        }
        return Response(payload, status=status.HTTP_200_OK)
    
    if request.method == 'POST':
        # Add to cart
        data = request.data
        item = data['item']
        
        # Check if item already exists in cart for user
        itemExists = Cart.objects.filter(user=request.user, menuitem=item).exists()
        if itemExists:
            # Update quantity
            cart_item = Cart.objects.get(user=request.user, menuitem=item)
            cart_item.quantity += 1
            cart_item.save()
            return Response(status=status.HTTP_200_OK)
        
        else:
            # Create new cart item
            menu_item = MenuItem.objects.get(id=item)
            cart_item = Cart.objects.create(user=request.user, menuitem=menu_item, quantity=1, unit_price=menu_item.price, price=menu_item.price)
            cart_item.save()
            return Response(status=status.HTTP_201_CREATED)
        
    if request.method == 'DELETE':
        # Delete all menu items in cart
        cart_items = Cart.objects.filter(user=request.user)
        cart_items.delete()
        return Response(status=status.HTTP_200_OK)
    

# Order management endpoints
@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def orders(request):
    # Manager
    isManager = request.user.groups.filter(name='Manager').exists()
    if isManager:
        if request.method == "GET":
            # Return all orders by all users
            orders = Order.objects.all()
            orders = OrderSerializer(orders, many=True).data
            return Response(orders, status=status.HTTP_200_OK)
        
    # Delivery Crew
    isDelivery = request.user.groups.filter(name='Delivery Crew').exists()
    if isDelivery:
        if request.method == "GET":
            orders = Order.objects.filter(delivery_crew=request.user)
            orders = OrderSerializer(orders, many=True).data
            result = {
                "total_orders": len(orders),
                "orders": orders
            }
            return Response(result, status=status.HTTP_200_OK)
    
    # Customer
    if request.method == "GET":
        # Return all orders by customer
        orders = Order.objects.filter(user=request.user)
        orders = OrderSerializer(orders, many=True).data
        result = {
            "count": len(orders),
            "orders": [order for order in orders]
        }
        return Response(result, status=status.HTTP_200_OK)
    
    if request.method == "POST":
        # Create new order from cart
        cart_items = Cart.objects.filter(user=request.user)
        if len(cart_items) == 0:
            # No items in cart
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        # Add them to order
        total_cost = sum([item.price for item in cart_items])
        new_order = Order.objects.create(user=request.user, status=False, total=total_cost, date=datetime.datetime.now())
        new_order.save()
        cart_items.delete()
        return Response(status=status.HTTP_201_CREATED)
            
    
@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def ordersId(request, orderId):
    # Handle manager actions
    isManager = request.user.groups.filter(name='Manager').exists()
    if isManager:
        if request.method == "DELETE":
            # Delete order if exists
            try:
                order = Order.objects.get(id=orderId)
                order.delete()
                return Response(status=status.HTTP_200_OK)
            except Exception as e:
                return Response(status=status.HTTP_404_NOT_FOUND)
        if request.method in ["PUT", "PATCH"]:
            # Update order
            data = request.data
            delivery_crew = User.objects.get(id=data['delivery-crew'])
            try:
                print("Found delivery crew", delivery_crew)
                order = Order.objects.get(id=orderId)
                order.delivery_crew = delivery_crew
                order.status = data['status']
                order.save()
                return Response(status=status.HTTP_200_OK)
            except Exception as e:
                return Response(status=status.HTTP_404_NOT_FOUND)
                
            
            
    # Handle delivery crew actions
    isDelivery = request.user.groups.filter(name='Delivery Crew').exists()
    if isDelivery:
        if request.method == "GET":
            # Update order status
            try:
                order = Order.objects.get(id=orderId)
                print(order.__dict__)
                # if order is not assigned to this delivery crew
                if order.delivery_crew_id != request.user.id:
                    return Response(order, status=status.HTTP_400_BAD_REQUEST)
                
                order.status = not order.status
                order.save()
                order = OrderSerializer(order).data
                return Response(order, status=status.HTTP_200_OK)
            except Exception as e:
                print(e)
                return Response(status=status.HTTP_404_NOT_FOUND)

# Helper functions
def get_all_menu_items():
    menu_items = MenuItem.objects.all()
    count = len(menu_items)
    menu_items = MenuItemSerializer(menu_items, many=True).data
   
    # Pagination
    results = [item for item in menu_items]
    payload = {
        'count': count,
        'next': "",
        'previous': "",
        'results': results
    }
    return payload