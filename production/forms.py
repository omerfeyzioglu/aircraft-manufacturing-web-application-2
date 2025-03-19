from django import forms
from django.contrib.auth.models import User
from .models import Team, Part, Aircraft, Production

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'team_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'team_type': forms.Select(attrs={'class': 'form-select'})
        }

class TeamMemberForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Kullanıcı'
    )

    def __init__(self, *args, **kwargs):
        team = kwargs.pop('team', None)
        super().__init__(*args, **kwargs)
        if team:
            self.fields['user'].queryset = User.objects.exclude(team_members=team)

class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ['name', 'team_type', 'stock']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'team_type': forms.Select(attrs={'class': 'form-select'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
        }

class ProductionForm(forms.ModelForm):
    class Meta:
        model = Production
        fields = ['part', 'quantity']
        widgets = {
            'part': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'})
        }

    def __init__(self, *args, **kwargs):
        team = kwargs.pop('team', None)
        super().__init__(*args, **kwargs)
        if team:
            self.fields['part'].queryset = Part.objects.filter(team_type=team.team_type)

class AircraftForm(forms.ModelForm):
    class Meta:
        model = Aircraft
        fields = ['aircraft_type']
        widgets = {
            'aircraft_type': forms.Select(attrs={'class': 'form-select'})
        }

    def clean(self):
        cleaned_data = super().clean()
        aircraft_type = cleaned_data.get('aircraft_type')
        if aircraft_type:
            # Aynı tipte üretimde olan uçak sayısını kontrol et
            in_production = Aircraft.objects.filter(
                aircraft_type=aircraft_type,
                completed_at__isnull=True
            ).count()
            if in_production >= 2:
                raise forms.ValidationError(
                    f'Bu tipte en fazla 2 uçak aynı anda üretimde olabilir. '
                    f'Şu anda {in_production} uçak üretimde.'
                )
        return cleaned_data 