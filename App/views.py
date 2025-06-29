from django.shortcuts import render
from .models import DailyData, MonthlyData
import datetime
from django.db.models import Sum

# Create your views here.
def index(request):
    # Get today's date
    today = datetime.date.today()
    
    # Get yesterday's date
    yesterday = today - datetime.timedelta(days=1)
    
    # Fetch daily data for yesterday
    daily_genartion_data = DailyData.objects.filter(date=yesterday,is_generation = True).first()
    daily_consumption_data = DailyData.objects.filter(date=yesterday,is_generation = False).first()

    # Fetch monthly data for the current month
    current_month = today.month
    current_year = today.year
    monthly_generation_data = MonthlyData.objects.filter(month=current_month, year=current_year, is_generation=True).first()
    monthly_consumption_data = MonthlyData.objects.filter(month=current_month, year=current_year, is_generation=False).first()
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