from django.db import models
from django.urls import reverse

# Create your models here.

class Worker(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    unavailable_dates = models.JSONField(default=list, blank=True)

    def is_available_on(self, date_obj):
        """
        date_obj: datetime.date
        returns True if worker is available on that date.
        """
        return date_obj.isoformat() not in (self.unavailable_dates or [])

    class Meta:
        ordering = ['last_name', 'first_name']
    
    def get_absolute_url(self):
        return reverse('detail_worker', args=[str(self.id)])
    
    def __str__(self):
        return f'{self.last_name} {self.first_name}'


class Schedule(models.Model):
    month = models.DateField()
    schedule = models.JSONField(default=dict)
    employee_stats = models.JSONField(default=dict)

    def get_absolute_url(self):
        return reverse('detail_schedule', args=[str(self.id)])

    def __str__(self):
        return f'{self.month} schedule'
    
    class Meta:
        ordering = ['month']
