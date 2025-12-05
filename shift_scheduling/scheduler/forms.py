from django import forms
from .models import Worker
from django.contrib.auth.forms import AuthenticationForm

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


class StyledAuthenticationForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-input-field'})
        self.fields['password'].widget.attrs.update({'class': 'form-input-field'})