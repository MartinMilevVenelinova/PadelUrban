from datetime import date, datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Pista(models.Model):
    """Representa una pista de pádel disponible en la comunidad."""

    nombre = models.CharField(max_length=100, unique=True)
    techada = models.BooleanField(default=False)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Pista'
        verbose_name_plural = 'Pistas'

    def __str__(self) -> str:
        tipo = 'Techada' if self.techada else 'Exterior'
        return f'{self.nombre} ({tipo})'


class Reserva(models.Model):
    """Representa la reserva de una pista de pádel por un vecino."""

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservas',
    )
    pista = models.ForeignKey(
        Pista,
        on_delete=models.CASCADE,
        related_name='reservas',
    )
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    class Meta:
        ordering = ['fecha', 'hora_inicio']
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'

    def __str__(self) -> str:
        pista_nombre = self.pista.nombre if self.pista_id else 'Sin pista'
        if self.fecha and self.hora_inicio and self.hora_fin:
            return (
                f'{pista_nombre} - {self.fecha} '
                f'({self.hora_inicio:%H:%M}-{self.hora_fin:%H:%M})'
            )
        return f'{pista_nombre} - Reserva incompleta'

    def duracion_minutos(self) -> int:
        """Calcula la duración de la reserva en minutos enteros."""
        if self.hora_inicio is None or self.hora_fin is None:
            return 0
        inicio = datetime.combine(date.min, self.hora_inicio)
        fin = datetime.combine(date.min, self.hora_fin)
        return int((fin - inicio).total_seconds() // 60)

    def clean(self) -> None:
        """Valida coherencia horaria y ausencia de solapamientos."""
        super().clean()

        if self.hora_inicio is None or self.hora_fin is None:
            return

        if self.hora_fin <= self.hora_inicio:
            raise ValidationError(
                {'hora_fin': 'La hora de fin debe ser posterior a la hora de inicio.'}
            )

        if self.pista_id is None or self.fecha is None:
            return

        solapadas = Reserva.objects.filter(
            pista_id=self.pista_id,
            fecha=self.fecha,
            hora_inicio__lt=self.hora_fin,
            hora_fin__gt=self.hora_inicio,
        )
        if self.pk is not None:
            solapadas = solapadas.exclude(pk=self.pk)

        if solapadas.exists():
            raise ValidationError(
                'La pista ya está reservada en ese tramo horario para la fecha indicada.'
            )
