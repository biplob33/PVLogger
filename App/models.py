from django.db import models
import datetime

# Create your models here.
class DailyData(models.Model):
    date = models.DateField(default=datetime.date.today() - datetime.timedelta(days=1))
    yesterday_data = models.FloatField()
    is_generation = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.date} ({'Generation' if self.is_generation else 'Consumption'})"
    
class MonthlyData(models.Model):
    MONTH_CHOICES = [
        (1, 'January'),
        (2, 'February'),
        (3, 'March'),
        (4, 'April'),
        (5, 'May'),
        (6, 'June'),
        (7, 'July'),
        (8, 'August'),
        (9, 'September'),
        (10, 'October'),
        (11, 'November'),
        (12, 'December'),
    ]
    month = models.IntegerField(choices=MONTH_CHOICES)
    months_generation = models.FloatField()
    year = models.IntegerField()
    is_generation = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{dict(self.MONTH_CHOICES).get(self.month, str(self.month))} ({'Generation' if self.is_generation else 'Consumption'})"