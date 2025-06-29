from django.shortcuts import render
from .models import DailyData, MonthlyData
import datetime
from django.db.models import Sum
from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib import messages

# Create your views here.
def index(request):
    # Get today's date
    today = datetime.date.today()
    
    # Get yesterday's date
    yesterday = today - datetime.timedelta(days=1)
    
    # Fetch daily data for yesterday
    daily_generation_obj = DailyData.objects.filter(date=yesterday, is_generation=True).first()
    daily_consumption_obj = DailyData.objects.filter(date=yesterday, is_generation=False).first()
    daily_genartion_data = daily_generation_obj.yesterday_data if daily_generation_obj else 0
    daily_consumption_data = daily_consumption_obj.yesterday_data if daily_consumption_obj else 0

    # Fetch monthly data for the current month
    current_month = today.month
    current_year = today.year
    monthly_generation_obj = MonthlyData.objects.filter(month=current_month, year=current_year, is_generation=True).first()
    monthly_consumption_obj = MonthlyData.objects.filter(month=current_month, year=current_year, is_generation=False).first()
    monthly_generation_data = monthly_generation_obj.months_generation if monthly_generation_obj else 0
    monthly_consumption_data = monthly_consumption_obj.months_generation if monthly_consumption_obj else 0
        
    # Calculate total generation and total consumption overall
    total_generation = DailyData.objects.filter(is_generation=True).aggregate(Sum('yesterday_data'))['yesterday_data__sum'] or 0
    total_consumption = DailyData.objects.filter(is_generation=False).aggregate(Sum('yesterday_data'))['yesterday_data__sum'] or 0
    
    # Prepare context for rendering
    context = {
        'daily_generation_data': daily_genartion_data,
        'daily_consumption_data': daily_consumption_data,
        'monthly_generation_data': monthly_generation_data,
        'monthly_consumption_data': monthly_consumption_data,
        'total_generation': total_generation,
        'total_consumption': total_consumption,
    }
    # Render the index.html template with the context
    return render(request, 'index.html', context)

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

    # Convert date string to date object
    date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
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