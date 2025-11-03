from django.db import models
from django.urls import reverse

# Create your models here.

class Worker(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    class Meta:
        ordering = ['last_name', 'first_name']
    
    def get_absolute_url(self):
        return reverse('detail-worker', args=[str(self.id)])
    
    def __str__(self):
        return f'{self.last_name}, {self.first_name}'
