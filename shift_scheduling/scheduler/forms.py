from django import forms
from .models import Worker
import json

class WorkerAvailabilityForm(forms.ModelForm):
    unavailable_dates_json = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Worker
        fields = []

    def clean_unavailable_dates_json(self):
        # get the string which represents json data 
        raw = self.cleaned_data.get('unavailable_dates_json', '') or '[]'
        
        try:
            # parse the string to create a python object (a list in this case)
            lst = json.loads(raw)
            cleaned = []
            # basic validation
            for d in lst:
                if not isinstance(d, str):
                    raise forms.ValidationError("Invalid date format.")
                if len(d) != 10:
                    raise forms.ValidationError("Invalid date format.")
                cleaned.append(d)
            cleaned = sorted(set(cleaned))

        except Exception:
            raise forms.ValidationError("Invalid JSON for unavailable dates.")

        # after running this method, form.cleaned_data.get('unavailable_dates_json')
        # return our cleaned variable

        return cleaned
    
    def save(self, commit=True):
        inst = super().save(commit=False)
        inst.unavailable_dates = self.cleaned_data.get('unavailable_dates_json', [])
        if commit:
            inst.save()
        return inst
    

class MonthForm(forms.Form):
    schedule_period = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'month'}),
        input_formats=['%Y-%m'],
        help_text='Choose scheduling period'
    )
