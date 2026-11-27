from django import forms

from .models import Pista, Reserva


class ReservaForm(forms.ModelForm):
    """Formulario de solicitud de reserva limitado a pistas activas."""

    class Meta:
        model = Reserva
        fields = ('pista', 'fecha', 'hora_inicio', 'hora_fin')
        widgets = {
            'pista': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pista'].queryset = Pista.objects.filter(activa=True)
