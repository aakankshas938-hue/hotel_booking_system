from django import forms
from .models import Booking, Review
from django.core.exceptions import ValidationError
import datetime

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['check_in_date', 'check_out_date', 'guests', 'special_requests']
        widgets = {
            'check_in_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'check_out_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'guests': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'special_requests': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in_date')
        check_out = cleaned_data.get('check_out_date')
        guests = cleaned_data.get('guests')
        
        if check_in and check_out:
            if check_in < datetime.date.today():
                raise ValidationError("Check-in date cannot be in the past.")
            
            if check_out <= check_in:
                raise ValidationError("Check-out date must be after check-in date.")
        
        if guests and (guests < 1 or guests > 10):
            raise ValidationError("Number of guests must be between 1 and 10.")
        
        return cleaned_data

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }