
from django.urls import path
from . import views

urlpatterns = [
    path('add_plane_type',views.add_plane_type,name="add_plane_type"),
    path('add_plane',views.add_plane,name="add_plane"),
    path('cancelflight',views.cancelflight,name="cancelflight"),
    path('add_flight',views.add_flight,name="add_flight"),
    path('getoccupancyrate',views.getoccupancyrate,name="getoccupancyrate"),
    path('net_profit',views.net_profit,name="net_profit"),
    path('manage_fares',views.manage_fares,name="manage_fares"),
    path('destinations',views.destinations,name="destinations"),
    path('manage_fareperkm',views.manage_fareperkm,name="manage_fareperkm")
]
