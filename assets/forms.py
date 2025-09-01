from django import forms
from .models import Asset

class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            'VPID', 'name', 'description',
            'category', 'location',
            'title_en', 'description_en',
            'title_de', 'description_de',
            'title_pl', 'description_pl',
            'image', 'is_active'  # 'is_active' tilføjes senere
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'description_en': forms.Textarea(attrs={'rows': 3}),
            'description_de': forms.Textarea(attrs={'rows': 3}),
            'description_pl': forms.Textarea(attrs={'rows': 3}),
        }
