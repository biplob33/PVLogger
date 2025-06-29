from django.contrib import admin
from .models import DailyData, MonthlyData
admin.site.register(DailyData)
admin.site.register(MonthlyData)