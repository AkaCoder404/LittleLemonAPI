from django.contrib import admin
from django.urls import path, include, re_path
from .views import *

urlpatterns = [
    path('menu-items/', view=menu_items, name='menu_items'),
    re_path(r'menu-items-page/$', view=menu_items_pag),
    path('categories/', view=categories, name='categories'),
    path('menu-items/<int:menuItem>', view=menu_item, name='menu_item'),
    path('groups/manager/users/', view=groups_manager_users, name='groups_manager_users'),
    path('groups/delivery-crew/users/', view=groups_delivery_crew_users, name='groups_delivery_crew_users'),
    path('groups/manager/users/<int:userId>', view=remove_manager, name='remove_manager'),
    
    
    path('groups/make_user_delivery_crew/', view=make_delivery_crew, name='make_delivery_crew'),
    path('cart/menu-items/', view=cart),
    path('orders/', view=orders),
    path('orders/<int:orderId>', view=ordersId),
]