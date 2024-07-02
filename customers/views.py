from django.shortcuts import render,redirect
from airplanes.models import airplanes,airplane_type,weeklyschedule
from .models import Tickets,currentflight,cancelled_tickets
from datetime import datetime,timedelta
import datetime
from datetime import *
import calendar
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User,auth
from django.views.decorators.cache import never_cache
from django.urls import reverse
import uuid
import json
from django.conf import settings
from django.core.mail import send_mail
import math


def index(request):
    print(4)
    # date_str = '2022-03-2'
    # my_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    # d = my_date+timedelta(days = 2)
    # print((my_date-d).days)
    
    if request.user.is_authenticated:
        if not request.user.is_staff:
            return render(request,'userpage.html',{'disable_back_button': True})
    return render(request,'ind.html')

def myfun(a):
    return a.departure_time


def search_flight(request):
    print(5)
    if request.method == 'POST':
        #print(request.POST)
        from_ = request.POST['from_']
        to_ = request.POST['to_']
        date_ = request.POST['date_']
        class_ = request.POST['class_']
        print(class_)
        date = datetime.strptime(date_, "%Y-%m-%d").date()
        day = date.strftime("%A")
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
        flights = weeklyschedule.objects.filter(departure = from_, destination = to_, day = day)
        list1 = []
        list2 = []
        for a in flights:
            curr_fli = currentflight()
            formatted_time = a.departure_time.strftime('%H:%M:%S')
            a.departure_time = formatted_time
            formatted_time = a.arrival_time.strftime('%H:%M:%S')
            a.arrival_time = formatted_time
            #formatted_date = date_.strftime('%Y-%m-%d')
            # forma3 = ticket.arrival_date.strftime('%Y-%m-%d')
            #ticket.arrival_date = forma3
            a.save()
            curr_fli.departure_time = a.departure_time
            curr_fli.arrival_time = a.arrival_time
            duration = a.arrival_day-day
            arrival_date = date+timedelta(days = duration)
            arrival = str(arrival_date)
            #arrival = datetime.datetime.strptime(arrival_date, "%Y-%m-%d").date()
            #print(date)
            curr_fli.plane_id = a.plane_id
            curr_fli.departure = a.departure
            curr_fli.destination = a.destination
            curr_fli.departure_date = date_
            curr_fli.arrival_date = arrival
            plane = airplanes.objects.get(plane_id = a.plane_id)
            curr_fli.type = plane.type
            plane_type = airplane_type.objects.get(type = plane.type)
            tickets1 = Tickets.objects.filter(plane_id = a.plane_id,departure_date = date_,departure_time = a.departure_time,seat_type = "economy")
            tickets2 = Tickets.objects.filter(plane_id = a.plane_id,departure_date = date_,departure_time = a.departure_time,seat_type = "business")
            tickets3 = Tickets.objects.filter(plane_id = a.plane_id,departure_date = date_,departure_time = a.departure_time,seat_type = "first")
            if plane_type.economy_seats:
                c_e = (a.distance*plane_type.fareperkm + plane_type.basic_cost)/plane_type.total_seats + plane.economy_price
            else:
                c_e = 0
            if plane_type.business_seats:
                c_b = (a.distance*plane_type.fareperkm + plane_type.basic_cost)/plane_type.total_seats + plane.business_price
            else:
                c_b = 0
            if plane_type.first_seats:
                c_f = (a.distance*plane_type.fareperkm + plane_type.basic_cost)/plane_type.total_seats + plane.first_price
            else:
                c_f = 0
            curr_fli.e_c = math.ceil(c_e)
            curr_fli.b_c = math.ceil(c_b)
            curr_fli.f_c = math.ceil(c_f)
            curr_fli.e_as = plane_type.economy_seats-len(tickets1)
            curr_fli.b_as = plane_type.business_seats-len(tickets2)
            curr_fli.f_as = plane_type.first_seats-len(tickets3)
            if class_ == "Economy":
                if plane_type.economy_seats-len(tickets1)>0:
                    list1.append(curr_fli)
                else:
                    if plane_type.business_seats-len(tickets2)>0 or plane_type.first_seats-len(tickets3)>0:
                        list2.append(curr_fli)
            elif class_ == "Business":
                if plane_type.business_seats-len(tickets2)>0:
                    list1.append(curr_fli)
                else:
                    if plane_type.economy_seats-len(tickets1)>0 or plane_type.first_seats-len(tickets3)>0:
                        list2.append(curr_fli)
            elif class_ == "First":
                if plane_type.first_seats-len(tickets3)>0:
                    list1.append(curr_fli)
                else:
                    if plane_type.business_seats-len(tickets2)>0 or plane_type.economy_seats-len(tickets1)>0:
                        list2.append(curr_fli)
        list1.sort(key=myfun)
        list2.sort(key=myfun)
        list1 = list1 + list2
        if len(list1):
            print(1000)
            return render(request,'available_flights.html',{'stu':1,'flight':list1,'ind':1,'seat_type':class_,'seat_no':0})
        else:
            print(2000)
            return render(request,'available_flights.html',{'flight':list1,'ind':0,'seat_type':class_,'seat_no':0})
    return render(request,'ind.html',{'disable_back_button': True})

def sn(request, seat_no):
    print(6)  
    
    if request.method == 'POST' :
        if request.POST['ind']== '1':
            plane_id = request.POST['plane_id']
            departure_date = request.POST['departure_date']
            departure_time = request.POST['departure_time']
            seat_type = request.POST['seat_type']
            p_s_n = request.POST['p_s_n']
            p_s_t = request.POST['p_s_t']
            plane = airplanes.objects.get(plane_id = plane_id)
            ext = 0
            if p_s_t == "economy":
                if seat_type == "business":
                    ext = plane.business_price-plane.economy_price
                elif seat_type == "first":
                    ext = plane.first_price-plane.economy_price
            elif p_s_t == "business":
                if seat_type == "economy":
                    ext = 0
                elif seat_type == "first":
                    ext = plane.first_price-plane.business_price
            else:
                ext = 0
            return render(request,'payment.html',{'ext':ext+500,'seat_no':seat_no,'seat_type':seat_type,'p_s_n':p_s_n,'p_s_t':p_s_t,'plane_id':plane_id,'departure_date':departure_date,'departure_time':departure_time})
        plane_id = request.POST['plane_id']
        departure = request.POST['departure']
        departure_date = request.POST['departure_date']
        departure_time = request.POST['departure_time']
        seat_type = request.POST['seat_type']
        cost = request.POST['cost']
        date = datetime.strptime(departure_date, "%Y-%m-%d").date()
        day = date.strftime("%A")
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
        plane =airplanes.objects.get(plane_id = plane_id)
        plane_type = airplane_type.objects.get(type = plane.type)
        duration = flight.arrival_day-day
        arrival_date = date+timedelta(days = duration)
        arrival = str(arrival_date)
        formatted_time = flight.departure_time.strftime('%H:%M:%S')
        flight.departure_time = formatted_time
        forma2 = flight.arrival_time.strftime('%H:%M:%S')
        flight.arrival_time = forma2
        flight.save()
        c_e = (flight.distance*plane_type.fareperkm + plane_type.basic_cost)/plane_type.total_seats + plane.economy_price + 500
        c_f = (flight.distance*plane_type.fareperkm + plane_type.basic_cost)/plane_type.total_seats + plane.first_price + 500
        c_b = (flight.distance*plane_type.fareperkm + plane_type.basic_cost)/plane_type.total_seats + plane.business_price + 500
        if seat_type == "economy":
            cost = c_e
        elif seat_type == "business":
            cost = c_b
        else:
            cost = c_f
        #request.session['current_page'] = request.path
        return render(request, 'ex.html',{'con':0,'flight':flight,'seat_no':seat_no,'seat_type':seat_type,'departure_date':departure_date,'arrival_date':arrival,'type':plane.type,'cost':math.ceil(cost)})
    if request.user.is_authenticated:
        return redirect('login')
    return render(request,'ind.html',{'disable_back_button': True})
    

#@login_required
def my(request):
    print(7)
    if request.POST.get('action')=='display':
        seat_type = request.POST['select']
        #user_id = request.POST['user_id']
        plane_id = request.POST['plane_id']
        departure = request.POST['departure']
        departure_date = request.POST['departure_date']
        departure_time = request.POST['departure_time']
        date = datetime.strptime(departure_date, "%Y-%m-%d").date()
        day = date.strftime("%A")
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
        list1 = []
        list2 = []
        list3 = []
        list4 = []
        flights = weeklyschedule.objects.get(departure = departure, day = day, plane_id = plane_id, departure_time = departure_time)
        formatted_time = flights.departure_time.strftime('%H:%M:%S')
        flights.departure_time = formatted_time
        flights.save()
        plane = airplanes.objects.get(plane_id = plane_id)
        planetype = airplane_type.objects.get(type = plane.type)
        
        if seat_type == "economy":
            #print(100)
            #cost = request.POST['e_c']          
            for i in range(1,planetype.economy_seats+1):
                list4.append(i)
                Ticket = Tickets.objects.filter(departure_date = departure_date,departure_time = departure_time,plane_id = plane_id,seat_type = seat_type,seat_no = i)
                if len(Ticket):
                    list1.append(i)
            my_list_json = json.dumps(list1)
            return render(request, 'seat.html',{'ind':0,'list':my_list_json,'seat_type':seat_type,'flight':flights,'departure_date':departure_date,'list4':list4})
        elif seat_type == "business":
            #print(200)
            #cost = request.POST['b_c']
            for i in range(1,planetype.business_seats+1):
                list4.append(i)
                Ticket = Tickets.objects.filter(departure_date = departure_date,departure_time = departure_time,plane_id = plane_id,seat_type = seat_type,seat_no = i)
                if len(Ticket):
                    list2.append(i)
            my_list_json = json.dumps(list2)
            return render(request, 'seat.html',{'ind':0,'list':my_list_json,'seat_type':seat_type,'flight':flights,'departure_date':departure_date,'list4':list4})
        #print(300)
        #cost = request.POST['f_c']
        for i in range(1,planetype.first_seats+1):
            list4.append(i)
            Ticket = Tickets.objects.filter(departure_date = departure_date,departure_time = departure_time,plane_id = plane_id,seat_type = seat_type,seat_no = i)
            if len(Ticket):
                list3.append(i)
        my_list_json = json.dumps(list3)
        return render(request, 'seat.html',{'ind':0,'list':my_list_json,'seat_type':seat_type,'flight':flights,'departure_date':departure_date,'list4':list4})
    #book_seat   
    elif request.POST.get('action')=='book':
        
        seat_type = request.POST['select']
        plane_id = request.POST['plane_id']
        departure = request.POST['departure']
        departure_date = request.POST['departure_date']
        departure_time = request.POST['departure_time']
        seat_no = request.POST['seat_no']
        
        print(seat_no)
        
        date = datetime.strptime(departure_date, "%Y-%m-%d").date()
        day = date.strftime("%A")
        
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
        flights = weeklyschedule.objects.get(departure = departure, day = day, plane_id = plane_id, departure_time = departure_time)
        formatted_time = flights.departure_time.strftime('%H:%M:%S')
        flights.departure_time = formatted_time
        forma2 = flights.arrival_time.strftime('%H:%M:%S')
        flights.arrival_time = forma2
        flights.save()
        duration = flights.arrival_day-day
        arrival_date = date+timedelta(days = duration)
        arrival = str(arrival_date)
        if request.user.is_authenticated: 
            #print(seat_no)
            upi = request.POST['upi']
            today  = date.today()
            print(today)
            duration = flights.arrival_day-day
            arrival_date = date+timedelta(days = duration)
            arrival = str(arrival_date)
            p = Tickets()
            p.departure_date = departure_date
            p.seat_type = seat_type
            p.plane_id = plane_id
            p.departure = departure
            p.departure_time = departure_time
            p.username = request.user.username
            p.destination = flights.destination
            p.arrival_time = flights.arrival_time
            p.booked_date = today
            p.arrival_date = arrival
            p.upi = upi
            flight = airplanes.objects.get(plane_id = plane_id)
            plane_type = airplane_type.objects.get(type = flight.type)
            p.distance = flights.distance
            print(flights.plane_id)
            if seat_type == "economy":
                num = plane_type.economy_seats
                cost = (flights.distance*plane_type.fareperkm + plane_type.basic_cost)/plane_type.total_seats + flight.economy_price
            if seat_type == "business":
                num = plane_type.business_seats
                cost = (flights.distance*plane_type.fareperkm + plane_type.basic_cost)/plane_type.total_seats + flight.business_price
            if seat_type == "first":
                num = plane_type.first_seats
                cost = (flights.distance*plane_type.fareperkm + plane_type.basic_cost)/plane_type.total_seats + flight.first_price
            if seat_no == "0":
                for i in range(1,num+1):
                    Ticket = Tickets.objects.filter(plane_id = plane_id,seat_type = seat_type, seat_no = i, departure = departure , departure_time = departure_time, departure_date = departure_date)
                    if len(Ticket)==0:
                        p.seat_no = i
                        p.cost = math.ceil(cost)
                        
                        p.save()
                        email = request.user.email
                        no = str(p.seat_no)
                        #print("booked")
                        #Set up email parameters
                        subject = 'Ticket'
                        message = 'Passenger name: '+ request.user.first_name + ' ' + request.user.last_name + '\nFrom: '+ departure + '\nTo: ' + p.destination + '\nDeparture date: ' + p.departure_date + '\nArrival date: ' + p.arrival_date + '\nDeparture time: ' + p.departure_time + '\nArrival time: ' + p.arrival_time + '\nSeat type: ' + p.seat_type + ' class' + '\nSeat number: ' + no + '\nDistance: ' + str(p.distance) + '\nCost: ' + str(math.ceil(p.cost))
                        from_email = 'indianeagleforu@gmail.com'
                        recipient_list = [email]

                        # Send email
                        send_mail(subject, message, from_email, recipient_list)
                        break
            else :
                p.seat_no = seat_no
                p.cost = math.ceil(cost) + 500
                subject = 'Ticket'
                message = 'Passenger name: '+ request.user.first_name + ' ' + request.user.last_name + '\nFrom: '+ departure + '\nTo: ' + p.destination + '\nDeparture date: ' + p.departure_date + '\nArrival date: ' + p.arrival_date + '\nDeparture time: ' + p.departure_time + '\nArrival time: ' + p.arrival_time + '\nSeat type: ' + p.seat_type + ' class' + '\nSeat number: ' + str(p.seat_no) + '\nDistance: ' + str(p.distance) + '\nCost: ' + str(math.ceil(p.cost))
                from_email = 'indianeagleforu@gmail.com'
                recipient_list = [request.user.email]

                # Send email
                send_mail(subject, message, from_email, recipient_list)
                p.save()
            print(p.booked_date)
            return render(request,'book_ticket.html')
        else:
            print(arrival_date)
            return render(request,'log.html',{'flight':flights,'ind':1,'seat_no':0,'seat_type':seat_type,'departure_date':departure_date,'arrival_date':arrival})
    elif request.POST.get('action')=='book1':
        print(10000)
        seat_type = request.POST['select']
        plane_id = request.POST['plane_id']
        departure = request.POST['departure']
        departure_date = request.POST['departure_date']
        departure_time = request.POST['departure_time']
        arrival_date = request.POST['arrival_date']
        date = datetime.strptime(departure_date, "%Y-%m-%d").date()
        day = date.strftime("%A")
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
        return render(request,'ex.html',{'ind':1,'con':1,'flight':flight,'seat_no':'0','seat_type':seat_type,'departure_date':departure_date,'arrival_date':arrival_date,'type':plane.type,'cost':math.ceil(cost)})
    if request.user.is_authenticated:
        return redirect('login')
    return render(request,'ind.html',{'disable_back_button': True})


def generate_pnr_number(plane_id,date,seat_type,seat_no):

    PNR = plane_id + date + seat_type[0]+seat_no
    print(PNR)


def my_bookings(request):
    if request.user.is_authenticated:
        t1 = []
        t2 = []
        now = datetime.now()
        today_date = now.date()
        print(type(today_date))
        tickets = Tickets.objects.filter(username = request.user.username)
        for ticket in tickets:
            dep_date = ticket.departure_date
            formatted_time = ticket.departure_time.strftime('%H:%M:%S')
            ticket.departure_time = formatted_time
            forma2 = ticket.arrival_time.strftime('%H:%M:%S')
            ticket.arrival_time = forma2
            formatted_date = ticket.departure_date.strftime('%Y-%m-%d')
            ticket.departure_date = formatted_date
            forma3 = ticket.arrival_date.strftime('%Y-%m-%d')
            ticket.arrival_date = forma3
            
            ticket.save()
            print(type(ticket.departure_date))
            if (dep_date-today_date).total_seconds()>86400:
                t2.append(ticket)
            else:
                t1.append(ticket)
        return render(request,'ticket.html',{'tickets1':t1,'tickets2':t2})
    return render(request,'ind.html')

def cancel_reservation(request):
    if request.POST.get('action')=='cancel':
        plane_id = request.POST['plane_id']
        departure = request.POST['departure']
        departure_date = request.POST['departure_date']
        departure_time = request.POST['departure_time']
        seat_type = request.POST['seat_type']
        seat_no = request.POST['seat_no']
        username = request.user.username
        ticket = Tickets.objects.get(username = username,plane_id = plane_id,departure_date = departure_date,departure_time = departure_time,seat_type = seat_type,seat_no = seat_no)
        can_t = cancelled_tickets()
        upi = ticket.upi
        cost = ticket.cost * 0.75
        ticket.cost = ticket.cost*0.25
        can_t.username = ticket.username
        can_t.plane_id = ticket.plane_id
        can_t.departure = ticket.departure
        can_t.destination = ticket,username
        can_t.departure_date = ticket.departure_date
        can_t.arrival_date = ticket.arrival_date
        can_t.booked_date = ticket.booked_date
        can_t.departure_time = ticket.departure_time
        can_t.arrival_time = ticket.arrival_time
        can_t.seat_type = ticket.seat_type
        can_t.seat_no = ticket.seat_no
        can_t.cost = ticket.cost
        can_t.distance = ticket.distance
        can_t.truth = 1
        can_t.save()
        ticket.delete()
        return render(request,'cancel_ticket.html',{'cost':math.ceil(cost),'upi':upi})
    elif request.POST.get('action')=='modify':
        plane_id = request.POST['plane_id']
        departure = request.POST['departure']
        departure_date = request.POST['departure_date']
        departure_time = request.POST['departure_time']
        seat_type = request.POST['seat_type']
        seat_no = request.POST['seat_no']
        username = request.user.username
        ticket = Tickets.objects.get(username = username,plane_id = plane_id,departure_date = departure_date,departure_time = departure_time,seat_type = seat_type,seat_no = seat_no)
        dep_date = ticket.departure_date
        formatted_time = ticket.departure_time.strftime('%H:%M:%S')
        ticket.departure_time = formatted_time
        forma2 = ticket.arrival_time.strftime('%H:%M:%S')
        ticket.arrival_time = forma2
        formatted_date = ticket.departure_date.strftime('%Y-%m-%d')
        ticket.departure_date = formatted_date
        forma3 = ticket.arrival_date.strftime('%Y-%m-%d')
        ticket.arrival_date = forma3
        ticket.save()
        curr_fli = currentflight()
        curr_fli.departure_time = ticket.departure_time
        curr_fli.arrival_time = ticket.arrival_time
        curr_fli.plane_id = ticket.plane_id
        curr_fli.departure = ticket.departure
        curr_fli.destination = ticket.destination
        curr_fli.departure_date = ticket.departure_date
        curr_fli.arrival_date = ticket.arrival_date
        plane = airplanes.objects.get(plane_id = ticket.plane_id)
        curr_fli.type = plane.type
        plane_type = airplane_type.objects.get(type = plane.type)
        tickets1 = Tickets.objects.filter(plane_id = ticket.plane_id,departure_date = ticket.departure_date,departure_time = ticket.departure_time,seat_type = "economy")
        tickets2 = Tickets.objects.filter(plane_id = ticket.plane_id,departure_date = ticket.departure_date,departure_time = ticket.departure_time,seat_type = "business")
        tickets3 = Tickets.objects.filter(plane_id = ticket.plane_id,departure_date = ticket.departure_date,departure_time = ticket.departure_time,seat_type = "first")
        # c_e = (ticket.distance*plane_type.fareperkm + plane_type.basic_cost)/plane_type.total_seats + plane.economy_price
        # c_b = (ticket.distance*plane_type.fareperkm + plane_type.basic_cost)/plane_type.total_seats + plane.business_price
        # c_f = (ticket.distance*plane_type.fareperkm + plane_type.basic_cost)/plane_type.total_seats + plane.first_price
        curr_fli.e_as = plane_type.economy_seats-len(tickets1)
        curr_fli.b_as = plane_type.business_seats-len(tickets2)
        curr_fli.f_as = plane_type.first_seats-len(tickets3)
        
        return render(request,'modify.html',{'ticket':ticket,'curr_f':curr_fli})
    return redirect('login')
    

def modify(request):
    if request.POST.get('action')=='change_seat':
        seat_type = request.POST['select']
        plane_id = request.POST['plane_id']
        departure_date = request.POST['departure_date']
        departure_time = request.POST['departure_time']
        username = request.user.username
        t_s_t = request.POST['t_s_t']
        seat_no = request.POST['seat_no']
        plane = airplanes.objects.get(plane_id = plane_id)
        planetype = airplane_type.objects.get(type = plane.type)
        list1 = []
        list2 = []
        list3 = []
        list4 = []
        print(504)
        if seat_type == "economy":         
            for i in range(1,planetype.economy_seats+1):
                list4.append(i)
                Ticket = Tickets.objects.filter(departure_date = departure_date,departure_time = departure_time,plane_id = plane_id,seat_type = seat_type,seat_no = i)
                if len(Ticket):
                    list1.append(i)
            my_list_json = json.dumps(list1)
            return render(request, 'modify_seat.html',{'ind':1,'list':my_list_json,'seat_type':seat_type,'departure_date':departure_date,'list4':list4,'ext':500,'p_s_n':seat_no,'p_s_t':t_s_t,'plane_id':plane_id,'departure_time':departure_time})
        elif seat_type == "business":
            for i in range(1,planetype.business_seats+1):
                list4.append(i)
                Ticket = Tickets.objects.filter(departure_date = departure_date,departure_time = departure_time,plane_id = plane_id,seat_type = seat_type,seat_no = i)
                if len(Ticket):
                    list2.append(i)
            my_list_json = json.dumps(list2)
            return render(request, 'modify_seat.html',{'ind':1,'list':my_list_json,'seat_type':seat_type,'departure_date':departure_date,'list4':list4,'ext':500,'p_s_n':seat_no,'p_s_t':t_s_t,'plane_id':plane_id,'departure_time':departure_time})

        for i in range(1,planetype.first_seats+1):
            list4.append(i)
            Ticket = Tickets.objects.filter(departure_date = departure_date,departure_time = departure_time,plane_id = plane_id,seat_type = seat_type,seat_no = i)
            if len(Ticket):
                list3.append(i)
        my_list_json = json.dumps(list3)
        return render(request, 'modify_seat.html',{'ind':1,'list':my_list_json,'seat_type':seat_type,'departure_date':departure_date,'list4':list4,'ext':500,'p_s_n':seat_no,'p_s_t':t_s_t,'plane_id':plane_id,'departure_time':departure_time})
    elif request.POST.get('action')=='save':
        seat_type = request.POST['select']
        plane_id = request.POST['plane_id']
        departure_date = request.POST['departure_date']
        departure_time = request.POST['departure_time']
        username = request.user.username
        t_s_t = request.POST['t_s_t']
        seat_no = request.POST['seat_no']
        ticket = Tickets.objects.get(username = username,plane_id = plane_id,departure_date = departure_date,departure_time = departure_time,seat_no = seat_no,seat_type = t_s_t)
        plane = airplanes.objects.get(plane_id = plane_id)
        plane_type = airplane_type.objects.get(type = plane.type)
        if seat_type == "economy":
            num = plane_type.economy_seats
            #cost = (flights.distance*plane_type.fareperkm + plane_type.basic_cost)/plane_type.total_seats + flight.economy_price
        if seat_type == "business":
            num = plane_type.business_seats
            #cost = (flights.distance*plane_type.fareperkm + plane_type.basic_cost)/plane_type.total_seats + flight.business_price
        if seat_type == "first":
            num = plane_type.first_seats
            #cost = (flights.distance*plane_type.fareperkm + plane_type.basic_cost)/plane_type.total_seats + flight.first_price
        for i in range(1,num+1):
            Ticket = Tickets.objects.filter(plane_id = plane_id,seat_type = seat_type, seat_no = i , departure_time = departure_time, departure_date = departure_date)
            if len(Ticket)==0:
                n_s_n = i
                if t_s_t == "economy":
                    if seat_type == "business":
                        ext = plane.business_price-plane.economy_price
                    else:
                        ext = plane.first_price-plane.economy_price
                elif t_s_t == "business":
                    if seat_type == "economy":
                        ext = 0
                    else:
                        ext = plane.first_price-plane.business_price
                else:
                    ext = 0
                break
        return render(request,'payment.html',{'ext':ext,'seat_no':n_s_n,'seat_type':seat_type,'p_s_n':seat_no,'p_s_t':t_s_t,'plane_id':plane_id,'departure_date':departure_date,'departure_time':departure_time})
    elif request.POST.get('action')=='change_Seat_no':
        plane_id = request.POST['plane_id']
        departure_date = request.POST['departure_date']
        departure_time = request.POST['departure_time']
        username = request.user.username
        t_s_t = request.POST['t_s_t']
        seat_no = request.POST['seat_no']
        seat_type = t_s_t
        plane = airplanes.objects.get(plane_id = plane_id)
        planetype = airplane_type.objects.get(type = plane.type)
        list1 = []
        list2 = []
        list3 = []
        list4 = []
        print(504)
        if t_s_t == "economy":         
            for i in range(1,planetype.economy_seats+1):
                list4.append(i)
                Ticket = Tickets.objects.filter(departure_date = departure_date,departure_time = departure_time,plane_id = plane_id,seat_type = seat_type,seat_no = i)
                if len(Ticket):
                    list1.append(i)
            my_list_json = json.dumps(list1)
            return render(request, 'modify_seat.html',{'ind':1,'list':my_list_json,'seat_type':t_s_t,'departure_date':departure_date,'list4':list4,'ext':500,'p_s_n':seat_no,'p_s_t':t_s_t,'plane_id':plane_id,'departure_time':departure_time})
        elif t_s_t == "business":
            for i in range(1,planetype.business_seats+1):
                list4.append(i)
                Ticket = Tickets.objects.filter(departure_date = departure_date,departure_time = departure_time,plane_id = plane_id,seat_type = seat_type,seat_no = i)
                if len(Ticket):
                    list2.append(i)
            my_list_json = json.dumps(list2)
            return render(request, 'modify_seat.html',{'ind':1,'list':my_list_json,'seat_type':t_s_t,'departure_date':departure_date,'list4':list4,'ext':500,'p_s_n':seat_no,'p_s_t':t_s_t,'plane_id':plane_id,'departure_time':departure_time})

        for i in range(1,planetype.first_seats+1):
            list4.append(i)
            Ticket = Tickets.objects.filter(departure_date = departure_date,departure_time = departure_time,plane_id = plane_id,seat_type = seat_type,seat_no = i)
            if len(Ticket):
                list3.append(i)
        my_list_json = json.dumps(list3)
        return render(request, 'modify_seat.html',{'ind':1,'list':my_list_json,'seat_type':t_s_t,'departure_date':departure_date,'list4':list4,'ext':500,'p_s_n':seat_no,'p_s_t':t_s_t,'plane_id':plane_id,'departure_time':departure_time})

def save_modify(request):
    print(request.POST)
    upi = request.POST['upi']
    plane_id = request.POST['plane_id']
    departure_date = request.POST['departure_date']
    departure_time = request.POST['departure_time']
    seat_type = request.POST['seat_type']
    p_s_n = request.POST['p_s_n']
    p_s_t = request.POST['p_s_t']
    seat_no = request.POST['seat_no']
    ext = request.POST['ext']
    username = request.user.username
    ticket = Tickets.objects.get(username = username,departure_date = departure_date,departure_time = departure_time,plane_id = plane_id,seat_no = p_s_n,seat_type = p_s_t)
    ticket.seat_no = seat_no
    ticket.seat_type = seat_type
    ticket.cost += float(ext)
    ticket.cost = math.ceil(ticket.cost)
    ticket.upi = upi
    ticket.save()
    return render(request,'modify_ticket.html')
