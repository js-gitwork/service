from django import forms
from .models import Asset, FaultReport

class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            'VPID', 'name', 'description', 'category', 'location',
            'image', 'is_active', 'last_inspection_date',
            'last_service_date', 'equipment'
        ]
        widgets = {
            'last_inspection_date': forms.DateInput(attrs={'type': 'date'}),
            'last_service_date': forms.DateInput(attrs={'type': 'date'}),
            'equipment': forms.CheckboxSelectMultiple,  # Pæn visning af udstyr
        }

class FaultReportForm(forms.ModelForm):
    class Meta:
        model = FaultReport
        fields = [
            'title', 'vpid', 'priority', 'description', 'original_description',
            'expected_workshop_date', 'mechanic_report', 'image'
        ]
        widgets = {
            'expected_workshop_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',  # Brug datetime-local for både dato og tid
                'class': 'form-control',
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Dansk beskrivelse af fejlen...'
            }),
            'original_description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Original beskrivelse (på brugerens sprog)...'
            }),
            'mechanic_report': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Reparationsrapport (hvad blev gjort?)...'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select',
            }),
        }
        labels = {
            'expected_workshop_date': 'Forventet indkaldelse til værksted',
        }
        help_texts = {
            'expected_workshop_date': 'Vælg dato og tid for når aktivet forventes på værksted.',
        }
