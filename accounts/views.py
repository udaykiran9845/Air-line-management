from django.shortcuts import render,redirect
from airplanes.models import airplanes,airplane_type,weeklyschedule
from django.contrib import messages
from django.contrib.auth.models import User,auth
from django.contrib.auth import authenticate,get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django_email_verification import send_email
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime,timedelta
import datetime
import math
# Create your views here.

@csrf_exempt
def register(request):
    print(1)
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        mail = request.POST['mail']
        user_id  = request.POST['user_id']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if first_name == "" or last_name == "" or user_id == "" or password1 == "" or password2 == "":
            messages.info(request, 'please fill all the details')
            return redirect('register')
        if password1 == password2:
            if User.objects.filter(username = user_id).exists():
                messages.info(request,'Username taken')
                return redirect('register')
            if User.objects.filter(email = mail).exists():
                messages.info(request,'email already exists')
                return redirect('register')
            else :
                u = User.objects.create_user(username=user_id,password=password1,email=mail,first_name = first_name,last_name = last_name)
                u.is_active = False
                u.save()
                send_email(u)
                return render(request,'check.html')
                #return render(request, 'home.html')
        else:
            messages.info(request,'password not matching')
            return redirect('register')
    else:
        return render(request, 'reg.html')



def login(request):
    print(2)
    if request.user.is_authenticated:
        if not request.user.is_staff:
            return render(request,'userpage.html',{'disable_back_button': True})
        else:
            return render(request,'adm.html',{'disable_back_button': True,'ind':0})
    if request.method == 'POST':
        if request.POST['ind']=='1':
            print(1000)
            seat_type = request.POST['seat_type']
            plane_id = request.POST['plane_id']
            departure = request.POST['departure']
            departure_date = request.POST['departure_date']
            departure_time = request.POST['departure_time']
            seat_no = request.POST['seat_no']
            arrival_date = request.POST['arrival_date']
            
            date = datetime.datetime.strptime(departure_date, "%Y-%m-%d").date()
            day = date.strftime("%A")
            print(seat_no)
            if day == "Monday":
                day = 0
            if day == "Tuesday":
                day = 1
            if day == "Wednesday":
                day = 2
            if day == "Thursday":
                day = 3
            if day == "Friday":
                day = 4
            if day == "Saturday":
                day = 5
            if day == "Sunday":
                day = 6 
            flight = weeklyschedule.objects.get(departure = departure, day = day, plane_id = plane_id, departure_time = departure_time)
            formatted_time = flight.departure_time.strftime('%H:%M:%S')
            flight.departure_time = formatted_time
            forma2 = flight.arrival_time.strftime('%H:%M:%S')
            flight.arrival_time = forma2
            flight.save()
            plane = airplanes.objects.get(plane_id = flight.plane_id)
            plane_type = airplane_type.objects.get(type = plane.type)
            c_e = (flight.distance*plane_type.fareperkm + plane_type.basic_cost)/plane_type.total_seats + plane.economy_price
            c_f = (flight.distance*plane_type.fareperkm + plane_type.basic_cost)/plane_type.total_seats + plane.first_price
            c_b = (flight.distance*plane_type.fareperkm + plane_type.basic_cost)/plane_type.total_seats + plane.business_price
            if seat_type == "economy":
                cost = c_e
            elif seat_type == "business":
                cost = c_b
            else:
                cost = c_f
            user_id  = request.POST['user_id']
            password = request.POST['password']
            user = authenticate(username = user_id,password = password)
            if user is not None:
                if user.is_staff:
                    auth.login(request,user)
                    return render(request,'adm.html',{'disable_back_button': True,'ind':0})
                auth.login(request,user)
                return render(request,'ex.html',{'ind':1,'con':1,'flight':flight,'seat_no':seat_no,'seat_type':seat_type,'departure_date':departure_date,'arrival_date':arrival_date,'type':plane.type,'cost':math.ceil(cost)})
            else:
                messages.info(request,'Invalid credentials')
                return redirect('login')
        user_id  = request.POST['user_id']
        password = request.POST['password']
        #print(1000)
        user = authenticate(username = user_id,password = password)
        if user is not None:
            #print(user.is_staff)
            if user.is_staff:
                auth.login(request,user)
                return render(request,'adm.html',{'disable_back_button': True,'ind':0})
            auth.login(request,user)
            # password = make_password('user.password')
            # print(password)
            # if request.user.is_authenticated:
            #      request.session['is_logged_in'] = True
            return render(request,'userpage.html',{'ind':0,'disable_back_button': True})
        else:
            messages.info(request,'Invalid credentials')
            return redirect('login')
    else:
        return render(request,'log.html',{'ind':0})
    

def logout(request):
    print(3)
    request.session['is_logged_in'] = False
    auth.logout(request)
    return render(request,'ind.html',{'disable_back_button': True})
