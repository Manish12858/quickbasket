from django import forms

from .models import Address


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ['user']
        labels = {
            'line1': 'Address line 1',
            'line2': 'Address line 2 (optional)',
            'postal_code': 'PIN / postal code',
        }
