from django.shortcuts import render,redirect
from .models import airplane_type,airplanes,weeklyschedule
from datetime import datetime,timedelta,date
from dateutil import rrule
from django.contrib import messages
from customers.models import Tickets,cancelled_tickets
# Create your views here.

def destinations(request):
    return render(request,'destinations.html')

def add_flight(request):
    departure = request.POST['departure']
    destination = request.POST['destination']
    if departure == destination:
        messages.info(request,'departure and destination cannot be same')
        return redirect('login')
    plane_id = request.POST['plane_id']
    departure_day = request.POST['departure_day']
    departure_time = request.POST['departure_time']
    arrival_day = request.POST['arrival_day']
    distance = request.POST['distance']
    arrival_time = request.POST['arrival_time']
    airplane = airplanes.objects.filter(plane_id = plane_id)
    if departure_day == arrival_day:
        if departure_time == arrival_time:
            messages.info(request,'departure time and arrival time cannot be same')
            return redirect('login')
    if len(airplane) == 0:
        messages.info(request,'plane doesnot exist')
        return redirect('login')
    tot_planes = weeklyschedule.objects.filter(plane_id = plane_id)
    if departure_day == "Monday":
        departure_day = 0
    if departure_day == "Tuesday":
        departure_day = 1
    if departure_day == "Wednesday":
        departure_day = 2
    if departure_day == "Thursday":
        departure_day = 3
    if departure_day == "Friday":
        departure_day = 4
    if departure_day == "Saturday":
        departure_day = 5
    if departure_day == "Sunday":
        departure_day = 6 
    if arrival_day == "Monday":
        arrival_day = 0
    if arrival_day == "Tuesday":
        arrival_day = 1
    if arrival_day == "Wednesday":
        arrival_day = 2
    if arrival_day == "Thursday":
        arrival_day = 3
    if arrival_day == "Friday":
        arrival_day = 4
    if arrival_day == "Saturday":
        arrival_day = 5
    if arrival_day == "Sunday":
        arrival_day = 6 
    stop = 0
    for plane in tot_planes:
        formatted_time = plane.departure_time.strftime('%H:%M:%S')
        plane.departure_time = formatted_time
        forma2 = plane.arrival_time.strftime('%H:%M:%S')
        plane.arrival_time = forma2
        # formatted_date = plane.departure_date.strftime('%Y-%m-%d')
        # plane.departure_date = formatted_date
        # forma3 = plane.arrival_date.strftime('%Y-%m-%d')
        # plane.arrival_date = forma3
        plane.save()
        if departure_day == plane.day:
            if departure_time < plane.departure_time:
                if arrival_day == plane.day and arrival_time < plane.departure_time:
                    continue
                else:
                    stop = 1
                    break
            elif departure_time > plane.arrival_time:
                continue
            else:
                stop = 1
                break
        elif departure_day < plane.day:
            if arrival_day <= plane.day:
                if arrival_day == plane.day:
                    if arrival_time >= plane.departure_time:
                        stop = 1
                        break
            else:
                stop = 1
                break
        else:
            if departure_day == plane.arrival_day:
                if departure_time <= plane.arrival_time:
                    stop = 1
                    break
            elif departure_day < plane.arrival_day:
                stop = 1
                break
    if stop == 1:
        messages.info(request,'flight unavailable in requested time')
        return redirect('login')

    gplanes = weeklyschedule.objects.filter(day = departure_day, departure = departure , departure_time = departure_time)
    lplanes = weeklyschedule.objects.filter(arrival_day = arrival_day, destination = destination , arrival_time = arrival_time)
    if len(gplanes) != 0 or len(lplanes) != 0:
        messages.info(request,'clash of timings')
        return redirect('login')

    new_s = weeklyschedule()
    new_s.day = departure_day
    new_s.departure = departure
    new_s.destination = destination
    new_s.departure_time = departure_time
    new_s.arrival_day = arrival_day
    new_s.arrival_time = arrival_time
    new_s.distance = distance
    new_s.plane_id = plane_id
    new_s.save()
    messages.info(request,'successfully added to the schedule')
    return redirect('login')

            


def add_plane_type(request):
    print(1000)
    type_ = request.POST['type_']
    e_s = request.POST['e_c']
    b_s = request.POST['b_c']
    f_s = request.POST['f_c']
    b_c = request.POST['basic_cost']
    fpkm = request.POST['fareperkm']
    
    plane_type = airplane_type.objects.filter(type = type_)
    if len(plane_type):
        messages.info(request,'flight type already exists')
        return redirect('login')

    new_pt = airplane_type()
    new_pt.type = type_
    new_pt.economy_seats = e_s
    new_pt.business_seats = b_s
    new_pt.first_seats = f_s
    new_pt.basic_cost = b_c
    new_pt.fareperkm = fpkm
    print(1)
    new_pt.total_seats = int(e_s) + int(b_s) + int(f_s)
    new_pt.save()
    messages.info(request,'successfully added')
    return redirect('login')
 

def add_plane(request):
    plane_id = request.POST['plane_id']
    type_ = request.POST['type_']
    ef = request.POST['economy_fare']
    bf = request.POST['business_fare']
    ff = request.POST['first_fare']
    plane_type = airplane_type.objects.filter(type = type_)
    if len(plane_type)==0:
        messages.info(request,'planetype does not exist')
        return redirect('login')
    plane = airplanes.objects.filter(plane_id = plane_id)
    if len(plane):
        messages.info(request,'plane id already exists')
        return redirect('login')
    new_p = airplanes()
    new_p.type = type_
    new_p.plane_id = plane_id
    new_p.economy_price = ef
    new_p.business_price = bf
    new_p.first_price = ff
    new_p.save()
    messages.info(request,'successfully added')
    return redirect('login')

def cancelflight(request) :  
    value1=request.POST['dayofweek']
    value2=request.POST['departuretime']
    value3=request.POST['flightid']
    if value1 == "Monday" or value1=="monday":
        t=0
    if value1 == "Tuesday" or value1=="tuesday":
        t=1
    if value1 == "Wednesday" or value1=="wednesday":  
        t=2
    if value1 == "Thursday" or value1=="thursday":  
            t=3
    if value1 == "Friday" or value1=="friday":  
            t=4
    if value1 == "Saturday" or value1=="saturday":  
            t=5
    if value1 == "Sunday" or value1=="sunday":  
        t=6
    my_objects = weeklyschedule.objects.filter(day=t,plane_id=value3,departure_time=value2)
    if len(my_objects)==0:
        messages.info(request,'No such flight exists')
        return redirect('login')
    else:
        my_objects.delete()
        messages.info(request,'successfully cancelled')
        return redirect('login')

# def net_profit(request):
#     from_ = request.POST['from_']
#     to_ = request.POST['to_']
#     duration = from_ - to_
#     for i in range(duration.days+1):
#         # date_str = '2022-03-2'
#         # my_date = datetime.strptime(date_str, '%Y-%m-%d').date()
#         d = from_+timedelta(days = i)
        
#         # print((my_date-d).days)
    
def getoccupancyrate(request):

    value1 = request.POST['departureplace']
    value2= request.POST['destiny']
    today = date.today()
    one_week_ago = today - timedelta(days=7)
    yesterday=today-timedelta(days=1)
    count1=0
    count2=0
    for dt in rrule.rrule(rrule.DAILY, dtstart=one_week_ago, until=today):
        dt = dt.strftime("%Y-%m-%d")
        My_objects1 = Tickets.objects.filter(departure=value1, destination=value2, departure_date = dt)
        count1+=len(My_objects1)
        array=[]
        for obj in My_objects1:
            if obj in array :
                continue 
            else:
                planes = airplanes.objects.get(plane_id = obj.plane_id)
                plane_type = airplane_type.objects.get(type = planes.type)
                if obj.plane_id == planes.plane_id:
                    if planes.type == plane_type.type: 
                        print(1000)  
                        count2+=plane_type.total_seats
            for obj1 in My_objects1:
                if obj1.departure_date==obj.departure_date and obj1.departure_time==obj.departure_time and obj1.departure==obj.departure:
                    array.append(obj1)
    if count2 == 0 :
        count3 = 0
    else:
        count3=count1/count2
    return render(request,'adm.html',{'ind':1,'occupancy':count3})

def net_profit(request):
    from_ = request.POST['from_']
    to_ = request.POST['to_']

    my_objects3 = Tickets.objects.filter(departure_date__range=(from_,to_), arrival_date__range=(from_,to_))
    total_revenue=0
    for obj in my_objects3 :
        total_revenue+=obj.cost
    my_objects4= cancelled_tickets.objects.filter(departure_date__range=(from_,to_), arrival_date__range=(from_,to_))

    for obj in my_objects4 :
        total_revenue+=obj.cost
    
    My_objects1 = Tickets.objects.filter( departure_date__range=(from_,to_), arrival_date__range=(from_,to_))
    My_objects2 = airplanes.objects.all()
    My_objects3 = airplane_type.objects.all()
    
    
    count2=0
    array=[]
    
    for obj in My_objects1:
        if obj in array :
            continue 
        else:
            print(type(obj.plane_id))
            planes = airplanes.objects.get(plane_id = obj.plane_id)
            print(100000)
            plane_type = airplane_type.objects.get(type = planes.type)
            
            if obj.plane_id == planes.plane_id:
                    if planes.type == plane_type.type:   
                        count2+=plane_type.basic_cost+obj.distance*plane_type.fareperkm
        for obj1 in My_objects1:
            if obj1.departure_date==obj.departure_date and obj1.departure_time==obj.departure_time and obj1.departure==obj.departure:
                array.append(obj1)
      
    net_profits=total_revenue-count2

    return render(request,'adm.html',{'ind':2,'profit':net_profits})

def manage_fares(request):
    flight_id = request.POST['flight_id']
    new_eco_fare = request.POST['new_eco_fare']
    new_buis_fare = request.POST['new_buis_fare']
    new_first_fare = request.POST['new_first_fare']
    if new_buis_fare == "" and new_eco_fare == "" and new_first_fare == "":
        messages.info(request,'Nothing to change')
        return redirect('login')
    myobjects=airplanes.objects.filter(plane_id=flight_id)
    if len(myobjects):
        if new_eco_fare != "":
            myobjects[0].economy_price=new_eco_fare
        if new_buis_fare != "":
            myobjects[0].business_price=new_buis_fare
        if new_first_fare != "":
            myobjects[0].first_price=new_first_fare
        myobjects[0].save()
        messages.info(request,'successfully changed')
        return redirect('login')
    messages.info(request,'plane doesnot exist')
    return redirect('login')

def manage_fareperkm(request):
    type = request.POST['type_']
    fpkm = request.POST['fpkm']
    bc = request.POST['bc']
    if bc == "" and fpkm == "":
        messages.info(request,'Nothing to change')
        return redirect('login')
    plane_type = airplane_type.objects.filter(type = type)
    if len(plane_type):
        if fpkm != "":
            plane_type[0].fareperkm = fpkm
        if bc != "":
            plane_type[0].basic_cost = bc
        plane_type[0].save()
        messages.info(request,'successfully changed')
        return redirect('login')
    messages.info(request,'planetype deos not exist')
    return redirect('login')