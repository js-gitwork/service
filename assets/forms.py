from django import forms
from .models import Asset

class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            'VPID', 'name', 'description', 'category', 'location',
            'image', 'qr_code', 'is_active', 'last_inspection_date',
            'last_service_date', 'equipment'
        ]
        widgets = {
            'last_inspection_date': forms.DateInput(attrs={'type': 'date'}),
            'last_service_date': forms.DateInput(attrs={'type': 'date'}),
            'equipment': forms.CheckboxSelectMultiple,  # Pæn visning af udstyr
        }
