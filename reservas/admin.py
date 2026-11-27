from django.contrib import admin

from .models import Pista, Reserva


@admin.register(Pista)
class PistaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'techada', 'activa')
    list_filter = ('techada', 'activa')
    search_fields = ('nombre',)


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('pista', 'usuario', 'fecha', 'hora_inicio', 'hora_fin')
    list_filter = ('fecha', 'pista')
    search_fields = ('usuario__username', 'pista__nombre')
