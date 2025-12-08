from django.db import models
from django.urls import reverse

# Create your models here.

class Worker(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    unavailable_dates = models.JSONField(default=list, blank=True)
    assign_least_shifts = models.BooleanField(default=False)
    assign_least_weekends = models.BooleanField(default=False)

    def is_available_on(self, date_obj):
        """
        date_obj: datetime.date
        returns True if worker is available on that date.
        """
        return date_obj.isoformat() not in (self.unavailable_dates or [])

    class Meta:
        ordering = ['last_name', 'first_name']
    
    def get_absolute_url(self):
        return reverse('worker_data', args=[str(self.id)])
    
    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Schedule(models.Model):
    schedule_period = models.DateField()
    per_day_schedule = models.JSONField(default=list)
    per_employee_schedule = models.JSONField(default=list)
    schedule_stats = models.JSONField(default=list)

    def get_absolute_url(self):
        return reverse('display_schedule', args=[str(self.id)])

    def __str__(self):
        return self.schedule_period.strftime("%B %Y")
    
    class Meta:
        ordering = ['-schedule_period']
