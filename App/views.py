from django.shortcuts import render
from .models import DailyData, MonthlyData
import datetime
from django.db.models import Sum
from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib import messages


def get_daily_data(request):
    if 'date' in request.GET:
        date_str = request.GET['date']
        query_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        query_date = datetime.date.today() - datetime.timedelta(days=1)
    
    # Fetch daily data for today
    daily_generation_obj = DailyData.objects.filter(date=query_date, is_generation=True).first()
    daily_consumption_obj = DailyData.objects.filter(date=query_date, is_generation=False).first()
    
    # Prepare data for response
    daily_generation_data = daily_generation_obj.yesterday_data if daily_generation_obj else 0
    daily_consumption_data = daily_consumption_obj.yesterday_data if daily_consumption_obj else 0

    prev_availble_data = DailyData.objects.filter(date=query_date - datetime.timedelta(days=1)).first()
    if prev_availble_data:
        prev_availble_data = True
    else:
        prev_availble_data = False
    # Prepare context for rendering
    context = {
        'generation_data': round(daily_generation_data, 2),
        'consumption_data': round(daily_consumption_data, 2),
        'prev_availble_data': prev_availble_data,
    }
    
    return JsonResponse(context)

def get_monthly_data(request):
    if 'date' in request.GET:
        date_str = request.GET['mnth']
        query_mnth = datetime.datetime.strptime(date_str, '%Y-%m').date().month
        query_year = datetime.datetime.strptime(date_str, '%Y-%m').date().year
    elif 'month' in request.GET and 'year' in request.GET:
        query_mnth = int(request.GET['month'])
        query_year = int(request.GET['year'])
    else:
        query_mnth = (datetime.date.today() - datetime.timedelta(days=1)).month
        query_year = (datetime.date.today() - datetime.timedelta(days=1)).year
    
    monthly_generation_obj = MonthlyData.objects.filter(month=query_mnth, year=query_year, is_generation=True).first()
    monthly_consumption_obj = MonthlyData.objects.filter(month=query_mnth, year=query_year, is_generation=False).first()
    monthly_generation_data = monthly_generation_obj.months_generation if monthly_generation_obj else 0
    monthly_consumption_data = monthly_consumption_obj.months_generation if monthly_consumption_obj else 0

    prev_month = query_mnth - 1 if query_mnth > 1 else 12
    prev_year = query_year if query_mnth > 1 else query_year - 1
    prev_availble_data = MonthlyData.objects.filter(month=prev_month, year=prev_year).exists()

    # Prepare context for rendering
    context = {
        'generation_data': round(monthly_generation_data, 2),
        'consumption_data': round(monthly_consumption_data, 2),
        'prev_availble_data': prev_availble_data,
    }
    
    return JsonResponse(context)

def get_total_data(request):
    total_generation = DailyData.objects.filter(is_generation=True).aggregate(Sum('yesterday_data'))['yesterday_data__sum'] or 0
    total_consumption = DailyData.objects.filter(is_generation=False).aggregate(Sum('yesterday_data'))['yesterday_data__sum'] or 0
    context = {
        'generation_data': round(total_generation, 2),
        'consumption_data': round(total_consumption, 2),
    }
    return JsonResponse(context)

def index(request):
    return render(request, 'index.html')

def monthly_data(request):
    if request.method == 'GET':
        month = request.GET.get('month')
        year = request.GET.get('year')
        if not month or not year:
            today = datetime.date.today()
            month = today.month
            year = today.year
        else:
            month = int(month)
            year = int(year)

        # Get daily data for the selected month and year
        daily_generation = DailyData.objects.filter(
            date__year=year, date__month=month, is_generation=True
        ).order_by('date')
        daily_consumption = DailyData.objects.filter(
            date__year=year, date__month=month, is_generation=False
        ).order_by('date')

        # Prepare data for plotting
        dates = [d.date.strftime('%Y-%m-%d') for d in daily_generation]
        generation_values = [float(d.yesterday_data) for d in daily_generation]
        consumption_values = [float(d.yesterday_data) for d in daily_consumption]

        context = {
            'month': month,
            'year': year,
            'dates': dates,
            'generation_values': generation_values,
            'consumption_values': consumption_values,
        }
        return JsonResponse(context)

def add_data(request):
    if request.method != 'POST':
        # If the request is not POST, redirect to index
        return render(request, 'add_data.html')
    date = request.POST.get('date')
    yesterday_generation_data = request.POST.get('yesterday_generation_data')
    yesterday_consumption_data = request.POST.get('yesterday_consumption_data')

    # Fetch the monthly generation data for the month and year of the selected date
    date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date() 
    # previous_date = date_obj - datetime.timedelta(days=1)
    month = date_obj.month
    year = date_obj.year
    # Calculate the sum of yesterday_data for the given month and year from DailyData
    monthly_generation_obj_sum = DailyData.objects.filter(
        date__year=year, is_generation=True
    ).exclude(date=date_obj).aggregate(Sum('yesterday_data'))['yesterday_data__sum'] or 0.0
    previous_generation_data = float(monthly_generation_obj_sum)
    # previous_generation_data = float(monthly_generation_obj_sum.months_generation) if monthly_generation_obj else 0.0

    # Subtract previous day's generation from the new generation data
    if yesterday_generation_data:
        yesterday_generation_data = round(float(yesterday_generation_data) - previous_generation_data, 2)
    else:
        yesterday_generation_data = 0.0

    # Fetch the monthly generation data for the month and year of the selected date (not previous_date)
    monthly_consumption_obj_sum = DailyData.objects.filter(
        date__year=year, is_generation=False
    ).exclude(date=date_obj).aggregate(Sum('yesterday_data'))['yesterday_data__sum'] or 0.0
    previous_consumption_data = float(monthly_consumption_obj_sum)
    # previous_consumption_data = float(monthly_consumptionn_obj.months_generation) if monthly_consumptionn_obj else 0.0

    # Subtract previous day's consumption from the new consumption data
    if yesterday_consumption_data:
        yesterday_consumption_data = round(float(yesterday_consumption_data) - previous_consumption_data, 2)
    else:
        yesterday_consumption_data = 0.0

    # Create or update DailyData for yesterday's generation
    DailyData.objects.update_or_create(
        date=date_obj,
        is_generation=True,
        defaults={'yesterday_data': yesterday_generation_data}
    )
    # Create or update DailyData for yesterday's consumption
    DailyData.objects.update_or_create(
        date=date_obj,
        is_generation=False,
        defaults={'yesterday_data': yesterday_consumption_data}
    )
    # Add monthly data if it doesn't exist or update it
    month = date_obj.month
    year = date_obj.year
    # Calculate total monthly generation data
    total_monthly_generation_data = DailyData.objects.filter(
        date__year=year, date__month=month, is_generation=True
    ).aggregate(Sum('yesterday_data'))['yesterday_data__sum'] or 0
    MonthlyData.objects.update_or_create(
        month=month,
        year=year,
        is_generation=True,
        defaults={'months_generation': total_monthly_generation_data}
    )
    # Calculate total monthly consumption data
    total_monthly_consumption_data = DailyData.objects.filter(
        date__year=year, date__month=month, is_generation=False
    ).aggregate(Sum('yesterday_data'))['yesterday_data__sum'] or 0
    MonthlyData.objects.update_or_create(
        month=month,
        year=year,
        is_generation=False,
        defaults={'months_generation': total_monthly_consumption_data}
    )
    # Set a success message in the session for middleware to pick up
    messages.success(request, 'Data added successfully!')
    return redirect('/')