from django.shortcuts import render, redirect
from datetime import datetime, timedelta
from .models import Booking
from django.contrib import messages

def index(request):
    return render(request, "index.html")

def valid_days(days):
    # Generate valid days for the next `days` days.
    today = datetime.now()
    valid_days = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]
    return valid_days

def filter_available_days(days):
   
    available_days = [day for day in days if Booking.objects.filter(day=day).count() < 5]
    return available_days

def filter_available_times(times, day):
    
    booked_times = Booking.objects.filter(day=day).values_list('time', flat=True)
    available_times = [time for time in times if time not in booked_times]
    return available_times

def day_to_weekday(day):
    
    return datetime.strptime(day, '%Y-%m-%d').strftime('%A')

def booking(request):
    
    days = valid_days(30)
    available_days = filter_available_days(days)

    if request.method == 'POST':
        host = request.POST.get('host')
        day = request.POST.get('day')

        if not host:
            messages.error(request, "Please select a host!")
            return redirect('booking')

        
        request.session['day'] = day
        request.session['host'] = host
        return redirect('booking_submit')

    return render(request, 'booking.html', {
        'days': days,
        'available_days': available_days,
    })

def booking_submit(request):
    user = request.user
    times = [
        "10:00 AM", "11:00 AM", "12:00 PM", "1:00 PM", "2:00 PM", "3:00 PM", "4:00 PM"
    ]

    today = datetime.now()
    min_date = today.strftime('%Y-%m-%d')
    max_date = (today + timedelta(days=30)).strftime('%Y-%m-%d')

    
    day = request.session.get('day')
    host = request.session.get('host')

    if not day or not host:
        messages.error(request, "Invalid session data. Please start your booking again.")
        return redirect('booking')

    available_times = filter_available_times(times, day)

    if request.method == 'POST':
        time = request.POST.get('time')
        weekday = day_to_weekday(day)

        if min_date <= day <= max_date:
            if Booking.objects.filter(day=day).count() < 5:
                if Booking.objects.filter(day=day, time=time).count() < 1:
                    Booking.objects.create(
                        user=user,
                        host=host,
                        day=day,
                        time=time,
                    )
                    messages.success(request, "Your booking has been confirmed!")
                    return redirect('index')
                else:
                    messages.error(request, "The selected time is already booked.")
            else:
                messages.error(request, "The selected day is fully booked.")
        else:
            messages.error(request, "The selected date is outside the allowed booking period.")

    return render(request, 'booking_submit.html', {
        'times': available_times,
    })
