
from django.urls import path
from . import views

urlpatterns = [
    path("",views.index,name = "index"),
    path('search_flight',views.search_flight,name="search_flight"),
    #path('book_seat',views.book_seat,name = "book_seat"),
    #path('display_seats',views.display_seats,name="display_seats"),
    path('my',views.my,name="my"),
    path('my_bookings', views.my_bookings, name="my_bookings"),
    path('customers/<int:seat_no>', views.sn, name='sn'),
    path('cancel_reservation',views.cancel_reservation,name="cancel_reservation"),
    path('modify',views.modify,name="modify"),
    path('save_modify',views.save_modify,name="save_modify")
]
