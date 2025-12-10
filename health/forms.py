from django import forms
from .models import HealthData

class HealthDataForm(forms.ModelForm):
    class Meta:
        model = HealthData
        fields = ["date", "heart_rate", "bmi", "sleep_hours", "notes"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}

    def clean_heart_rate(self):
        hr = self.cleaned_data["heart_rate"]
        if hr <= 0:
            raise forms.ValidationError("Heart rate must be positive.")
        return hr
