from django import forms
from .models import Worker

class WorkerDataForm(forms.ModelForm):

    class Meta:
        model = Worker
        fields = [
            'unavailable_dates',
            'first_name',
            'last_name',
            'assign_least_shifts',
            'assign_least_weekends',
        ]
        
        widgets = {
            'unavailable_dates': forms.HiddenInput(),
            'first_name': forms.TextInput(attrs={'class': 'form-input-field'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input-field'}),
            'assign_least_shifts': forms.CheckboxInput(),
            'assign_least_weekends': forms.CheckboxInput(),
        }


class MonthForm(forms.Form):
    schedule_period = forms.DateField(
        label="Select month",
        widget=forms.DateInput(attrs={'type': 'month', 'class': 'form-input-field'}),
        input_formats=['%Y-%m'],
        help_text='Choose scheduling period'
    )