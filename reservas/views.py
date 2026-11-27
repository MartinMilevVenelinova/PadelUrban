from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ReservaForm
from .models import Reserva


def registro(request):
    """Registra un nuevo vecino usando UserCreationForm y redirige al login."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro completado. Ya puedes iniciar sesión.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'reservas/registro.html', {'form': form})


@login_required
def reservas_inicio(request):
    """Lista todas las reservas en orden cronológico."""
    reservas = Reserva.objects.select_related('pista', 'usuario').all()
    return render(request, 'reservas/reservas_list.html', {'reservas': reservas})


@login_required
def reserva_crear(request):
    """Crea una reserva asignando automáticamente el usuario autenticado."""
    if request.method == 'POST':
        instancia = Reserva(usuario=request.user)
        form = ReservaForm(request.POST, instance=instancia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reserva creada correctamente.')
            return redirect('reservas')
        messages.error(request, 'No se pudo crear la reserva. Revisa los errores.')
    else:
        form = ReservaForm()
    return render(request, 'reservas/reserva_form.html', {'form': form})


@login_required
@require_POST
def reserva_cancelar(request, pk):
    """Cancela una reserva únicamente si pertenece al usuario autenticado."""
    reserva = get_object_or_404(Reserva, pk=pk)
    if reserva.usuario != request.user:
        return HttpResponseForbidden('No tienes permiso para cancelar esta reserva.')
    reserva.delete()
    messages.success(request, 'Reserva cancelada correctamente.')
    return redirect('reservas')
