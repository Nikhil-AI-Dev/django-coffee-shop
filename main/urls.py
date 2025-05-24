from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from .views import download_receipt
from .views import admin_dashboard
from .views import export_orders_csv

urlpatterns = [
    path('', views.home, name='home'),
    path('menu/', views.menu, name='menu'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('locations/', views.locations, name='locations'),
    path('order/', views.place_order, name='order'),
    path('myorders/', views.my_orders, name='my_orders'),
    path('order/thankyou/<int:order_id>/', views.thank_you, name='thank_you'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('search/', views.search_view, name='search'),
    path('receipt/<int:order_id>/download/', views.download_receipt, name='download_receipt'),
    path('receipt/<int:order_id>/', views.download_receipt, name='download_receipt'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/export-csv/', export_orders_csv, name='export_orders_csv'),
   

]

