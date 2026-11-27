from datetime import date, time

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Pista, Reserva

User = get_user_model()


class PistaYReservaModelTests(TestCase):
    def setUp(self) -> None:
        self.usuario1 = User.objects.create_user(username='vecino1', password='Password123!')
        self.usuario2 = User.objects.create_user(username='vecino2', password='Password123!')
        self.pista1 = Pista.objects.create(nombre='Pista 1', techada=True, activa=True)
        self.pista2 = Pista.objects.create(nombre='Pista 2', techada=False, activa=True)
        self.fecha = date(2026, 12, 1)

    def test_duracion_minutos(self) -> None:
        reserva = Reserva(
            usuario=self.usuario1,
            pista=self.pista1,
            fecha=self.fecha,
            hora_inicio=time(10, 0),
            hora_fin=time(11, 30),
        )
        self.assertEqual(reserva.duracion_minutos(), 90)

    def test_str_modelos(self) -> None:
        self.assertEqual(str(self.pista1), 'Pista 1 (Techada)')
        reserva = Reserva(
            usuario=self.usuario1,
            pista=self.pista2,
            fecha=self.fecha,
            hora_inicio=time(17, 0),
            hora_fin=time(18, 0),
        )
        self.assertIn('Pista 2', str(reserva))
        self.assertIn('17:00-18:00', str(reserva))

    def test_horarios_invalidos_fallan_full_clean(self) -> None:
        reserva_igual = Reserva(
            usuario=self.usuario1,
            pista=self.pista1,
            fecha=self.fecha,
            hora_inicio=time(10, 0),
            hora_fin=time(10, 0),
        )
        with self.assertRaises(ValidationError):
            reserva_igual.full_clean()

        reserva_anterior = Reserva(
            usuario=self.usuario1,
            pista=self.pista1,
            fecha=self.fecha,
            hora_inicio=time(12, 0),
            hora_fin=time(11, 0),
        )
        with self.assertRaises(ValidationError):
            reserva_anterior.full_clean()

    def test_solapamientos_fallan_full_clean(self) -> None:
        Reserva.objects.create(
            usuario=self.usuario1,
            pista=self.pista1,
            fecha=self.fecha,
            hora_inicio=time(10, 0),
            hora_fin=time(11, 30),
        )
        tramos_solapados = [
            (time(10, 0), time(11, 30)),
            (time(9, 30), time(10, 30)),
            (time(11, 0), time(12, 0)),
            (time(10, 15), time(11, 0)),
            (time(9, 0), time(12, 0)),
        ]
        for inicio, fin in tramos_solapados:
            candidata = Reserva(
                usuario=self.usuario2,
                pista=self.pista1,
                fecha=self.fecha,
                hora_inicio=inicio,
                hora_fin=fin,
            )
            with self.assertRaises(ValidationError):
                candidata.full_clean()

    def test_reservas_consecutivas_permitidas(self) -> None:
        Reserva.objects.create(
            usuario=self.usuario1,
            pista=self.pista1,
            fecha=self.fecha,
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0),
        )
        siguiente = Reserva(
            usuario=self.usuario2,
            pista=self.pista1,
            fecha=self.fecha,
            hora_inicio=time(11, 0),
            hora_fin=time(12, 0),
        )
        siguiente.full_clean()
        siguiente.save()

        anterior = Reserva(
            usuario=self.usuario2,
            pista=self.pista1,
            fecha=self.fecha,
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
        )
        anterior.full_clean()
        anterior.save()
        self.assertEqual(Reserva.objects.count(), 3)

    def test_distintas_pistas_y_fechas_permitidas(self) -> None:
        Reserva.objects.create(
            usuario=self.usuario1,
            pista=self.pista1,
            fecha=self.fecha,
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0),
        )
        otra_pista = Reserva(
            usuario=self.usuario2,
            pista=self.pista2,
            fecha=self.fecha,
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0),
        )
        otra_pista.full_clean()

        otra_fecha = Reserva(
            usuario=self.usuario2,
            pista=self.pista1,
            fecha=date(2026, 12, 2),
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0),
        )
        otra_fecha.full_clean()

    def test_edicion_sin_conflicto_consigo_misma(self) -> None:
        reserva = Reserva.objects.create(
            usuario=self.usuario1,
            pista=self.pista1,
            fecha=self.fecha,
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0),
        )
        reserva.hora_fin = time(11, 30)
        reserva.full_clean()
        reserva.save()
        reserva.refresh_from_db()
        self.assertEqual(reserva.duracion_minutos(), 90)

    def test_campos_incompletos_no_lanzan_excepcion_inesperada(self) -> None:
        incompleta = Reserva()
        incompleta.clean()
        with self.assertRaises(ValidationError):
            incompleta.full_clean()


from django.urls import reverse


class AutenticacionTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='vecino_existente',
            password='PasswordSegura123!',
        )

    def test_registro_valido_y_password_hasheada(self) -> None:
        response = self.client.post(
            reverse('registro'),
            {
                'username': 'vecino_nuevo',
                'password1': 'ClaveMuySegura99!',
                'password2': 'ClaveMuySegura99!',
            },
        )
        self.assertRedirects(response, reverse('login'))
        nuevo = User.objects.get(username='vecino_nuevo')
        self.assertNotEqual(nuevo.password, 'ClaveMuySegura99!')
        self.assertTrue(nuevo.password.startswith('pbkdf2_'))
        self.assertTrue(nuevo.check_password('ClaveMuySegura99!'))

    def test_registro_usuario_duplicado(self) -> None:
        response = self.client.post(
            reverse('registro'),
            {
                'username': 'vecino_existente',
                'password1': 'ClaveMuySegura99!',
                'password2': 'ClaveMuySegura99!',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'errorlist')
        self.assertEqual(User.objects.filter(username='vecino_existente').count(), 1)

    def test_registro_contrasenas_invalidas(self) -> None:
        response_distintas = self.client.post(
            reverse('registro'),
            {
                'username': 'otro_vecino',
                'password1': 'ClaveMuySegura99!',
                'password2': 'OtraClave99!',
            },
        )
        self.assertEqual(response_distintas.status_code, 200)
        self.assertContains(response_distintas, 'errorlist')
        self.assertFalse(User.objects.filter(username='otro_vecino').exists())

        response_debil = self.client.post(
            reverse('registro'),
            {
                'username': 'otro_vecino',
                'password1': '1234',
                'password2': '1234',
            },
        )
        self.assertEqual(response_debil.status_code, 200)
        self.assertContains(response_debil, 'errorlist')
        self.assertFalse(User.objects.filter(username='otro_vecino').exists())

    def test_login_correcto_e_incorrecto(self) -> None:
        resp_mal = self.client.post(
            reverse('login'),
            {'username': 'vecino_existente', 'password': 'Incorrecta'},
        )
        self.assertEqual(resp_mal.status_code, 200)
        self.assertFalse(resp_mal.wsgi_request.user.is_authenticated)

        resp_ok = self.client.post(
            reverse('login'),
            {'username': 'vecino_existente', 'password': 'PasswordSegura123!'},
        )
        self.assertRedirects(resp_ok, reverse('reservas'))

    def test_logout_post(self) -> None:
        self.client.force_login(self.user)
        resp_get = self.client.get(reverse('logout'))
        self.assertEqual(resp_get.status_code, 405)

        resp_post = self.client.post(reverse('logout'))
        self.assertRedirects(resp_post, reverse('login'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_bloqueo_anonimo_reservas_y_raiz(self) -> None:
        resp_reservas = self.client.get(reverse('reservas'))
        self.assertRedirects(
            resp_reservas,
            f"{reverse('login')}?next={reverse('reservas')}",
        )

        resp_raiz = self.client.get(reverse('inicio'))
        self.assertRedirects(
            resp_raiz,
            reverse('reservas'),
            fetch_redirect_response=False,
        )


from django.test import Client


class ReservasCRUDTests(TestCase):
    def setUp(self) -> None:
        self.user1 = User.objects.create_user(username='vecino_a', password='Password123!')
        self.user2 = User.objects.create_user(username='vecino_b', password='Password123!')
        self.pista_activa = Pista.objects.create(nombre='Pista Activa', techada=True, activa=True)
        self.pista_inactiva = Pista.objects.create(nombre='Pista Inactiva', techada=False, activa=False)
        self.fecha = date(2026, 12, 10)

    def test_listado_cronologico_y_diferenciacion_propias(self) -> None:
        r2 = Reserva.objects.create(
            usuario=self.user2,
            pista=self.pista_activa,
            fecha=self.fecha,
            hora_inicio=time(18, 0),
            hora_fin=time(19, 30),
        )
        r1 = Reserva.objects.create(
            usuario=self.user1,
            pista=self.pista_activa,
            fecha=self.fecha,
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0),
        )
        self.client.force_login(self.user1)
        resp = self.client.get(reverse('reservas'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(list(resp.context['reservas']), [r1, r2])
        self.assertContains(resp, '60 min')
        self.assertContains(resp, '90 min')
        self.assertContains(resp, 'Tu reserva')
        self.assertContains(resp, reverse('reserva_cancelar', args=[r1.pk]))
        self.assertNotContains(resp, reverse('reserva_cancelar', args=[r2.pk]))

    def test_asignacion_automatica_y_resistencia_suplantacion(self) -> None:
        self.client.force_login(self.user1)
        resp = self.client.post(
            reverse('reserva_crear'),
            {
                'usuario': self.user2.pk,
                'pista': self.pista_activa.pk,
                'fecha': '2026-12-10',
                'hora_inicio': '10:00',
                'hora_fin': '11:00',
            },
        )
        self.assertRedirects(resp, reverse('reservas'))
        reserva = Reserva.objects.get()
        self.assertEqual(reserva.usuario, self.user1)

    def test_horarios_invalidos_y_solapamiento_no_guardan(self) -> None:
        Reserva.objects.create(
            usuario=self.user2,
            pista=self.pista_activa,
            fecha=self.fecha,
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0),
        )
        self.client.force_login(self.user1)

        resp_hora = self.client.post(
            reverse('reserva_crear'),
            {
                'pista': self.pista_activa.pk,
                'fecha': '2026-12-10',
                'hora_inicio': '12:00',
                'hora_fin': '11:00',
            },
        )
        self.assertEqual(resp_hora.status_code, 200)
        self.assertContains(resp_hora, 'errorlist')
        self.assertEqual(Reserva.objects.count(), 1)

        resp_solape = self.client.post(
            reverse('reserva_crear'),
            {
                'pista': self.pista_activa.pk,
                'fecha': '2026-12-10',
                'hora_inicio': '10:30',
                'hora_fin': '11:30',
            },
        )
        self.assertEqual(resp_solape.status_code, 200)
        self.assertContains(resp_solape, 'errorlist')
        self.assertEqual(Reserva.objects.count(), 1)

    def test_consecutivas_validas_y_rechazo_pista_inactiva(self) -> None:
        Reserva.objects.create(
            usuario=self.user2,
            pista=self.pista_activa,
            fecha=self.fecha,
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0),
        )
        self.client.force_login(self.user1)

        resp_consecutiva = self.client.post(
            reverse('reserva_crear'),
            {
                'pista': self.pista_activa.pk,
                'fecha': '2026-12-10',
                'hora_inicio': '11:00',
                'hora_fin': '12:00',
            },
        )
        self.assertRedirects(resp_consecutiva, reverse('reservas'))
        self.assertEqual(Reserva.objects.count(), 2)

        resp_inactiva = self.client.post(
            reverse('reserva_crear'),
            {
                'pista': self.pista_inactiva.pk,
                'fecha': '2026-12-10',
                'hora_inicio': '12:00',
                'hora_fin': '13:00',
            },
        )
        self.assertEqual(resp_inactiva.status_code, 200)
        self.assertContains(resp_inactiva, 'errorlist')
        self.assertEqual(Reserva.objects.count(), 2)

    def test_cancelacion_propia_y_bloqueo_ajena(self) -> None:
        propia = Reserva.objects.create(
            usuario=self.user1,
            pista=self.pista_activa,
            fecha=self.fecha,
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0),
        )
        ajena = Reserva.objects.create(
            usuario=self.user2,
            pista=self.pista_activa,
            fecha=self.fecha,
            hora_inicio=time(11, 0),
            hora_fin=time(12, 0),
        )
        self.client.force_login(self.user1)

        resp_ajena = self.client.post(reverse('reserva_cancelar', args=[ajena.pk]))
        self.assertEqual(resp_ajena.status_code, 403)
        self.assertTrue(Reserva.objects.filter(pk=ajena.pk).exists())

        resp_propia = self.client.post(reverse('reserva_cancelar', args=[propia.pk]))
        self.assertRedirects(resp_propia, reverse('reservas'))
        self.assertFalse(Reserva.objects.filter(pk=propia.pk).exists())

    def test_get_cancelar_sin_borrado_y_acceso_anonimo_bloqueado(self) -> None:
        reserva = Reserva.objects.create(
            usuario=self.user1,
            pista=self.pista_activa,
            fecha=self.fecha,
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0),
        )
        for url in (
            reverse('reservas'),
            reverse('reserva_crear'),
            reverse('reserva_cancelar', args=[reserva.pk]),
        ):
            resp = self.client.get(url)
            self.assertRedirects(resp, f"{reverse('login')}?next={url}")

        self.client.force_login(self.user1)
        resp_get = self.client.get(reverse('reserva_cancelar', args=[reserva.pk]))
        self.assertEqual(resp_get.status_code, 405)
        self.assertTrue(Reserva.objects.filter(pk=reserva.pk).exists())

    def test_post_sin_csrf_rechazado(self) -> None:
        reserva = Reserva.objects.create(
            usuario=self.user1,
            pista=self.pista_activa,
            fecha=self.fecha,
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0),
        )
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.user1)

        resp_crear = csrf_client.post(
            reverse('reserva_crear'),
            {
                'pista': self.pista_activa.pk,
                'fecha': '2026-12-10',
                'hora_inicio': '11:00',
                'hora_fin': '12:00',
            },
        )
        self.assertEqual(resp_crear.status_code, 403)
        self.assertEqual(Reserva.objects.count(), 1)

        resp_cancelar = csrf_client.post(reverse('reserva_cancelar', args=[reserva.pk]))
        self.assertEqual(resp_cancelar.status_code, 403)
        self.assertTrue(Reserva.objects.filter(pk=reserva.pk).exists())


class SeguridadTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='vecino_seg', password='PasswordSegura123!')
        self.staff = User.objects.create_user(
            username='admin_seg',
            password='PasswordSegura123!',
            is_staff=True,
            is_superuser=True,
        )

    def test_bloqueo_temporal_axes_login_admin_y_proxy(self) -> None:
        for _ in range(4):
            resp = self.client.post(
                reverse('login'),
                {'username': 'vecino_seg', 'password': 'WrongPassword'},
            )
            self.assertEqual(resp.status_code, 200)

        resp_lock = self.client.post(
            reverse('login'),
            {'username': 'vecino_seg', 'password': 'WrongPassword'},
        )
        self.assertEqual(resp_lock.status_code, 429)
        self.assertContains(resp_lock, 'Acceso bloqueado temporalmente', status_code=429)

        # Incluso con contraseña válida o cabecera proxy falsa sigue bloqueado
        resp_proxy = self.client.post(
            reverse('login'),
            {'username': 'vecino_seg', 'password': 'PasswordSegura123!'},
            HTTP_X_FORWARDED_FOR='203.0.113.99',
        )
        self.assertEqual(resp_proxy.status_code, 429)

        # Bloqueo también activo en /admin/login/ para esa combinación usuario/IP
        resp_admin_lock = self.client.post(
            '/admin/login/',
            {'username': 'vecino_seg', 'password': 'PasswordSegura123!'},
        )
        self.assertEqual(resp_admin_lock.status_code, 429)

        # Otro usuario desde la misma IP no queda bloqueado
        resp_otro = self.client.post(
            reverse('login'),
            {'username': 'admin_seg', 'password': 'PasswordSegura123!'},
        )
        self.assertRedirects(resp_otro, reverse('reservas'))

    def test_redireccion_externa_next_bloqueada(self) -> None:
        resp = self.client.post(
            f"{reverse('login')}?next=https://evil.example/phish",
            {'username': 'vecino_seg', 'password': 'PasswordSegura123!'},
        )
        self.assertRedirects(resp, reverse('reservas'))

    def test_errores_login_no_revelan_existencia_cuenta(self) -> None:
        resp_existe = self.client.post(
            reverse('login'),
            {'username': 'vecino_seg', 'password': 'Incorrecta'},
        )
        resp_no_existe = self.client.post(
            reverse('login'),
            {'username': 'no_existe_xyz', 'password': 'Incorrecta'},
        )
        self.assertEqual(
            list(resp_existe.context['form'].non_field_errors()),
            list(resp_no_existe.context['form'].non_field_errors()),
        )

    def test_escape_html_en_plantillas(self) -> None:
        pista_xss = Pista.objects.create(
            nombre='<script>alert("xss")</script>',
            techada=False,
            activa=True,
        )
        Reserva.objects.create(
            usuario=self.user,
            pista=pista_xss,
            fecha=date(2026, 12, 20),
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0),
        )
        self.client.force_login(self.user)
        resp = self.client.get(reverse('reservas'))
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, '<script>alert("xss")</script>')
        self.assertContains(resp, '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;')

    def test_recuperacion_tras_enfriamiento_axes(self) -> None:
        from datetime import timedelta
        from django.utils import timezone
        from axes.models import AccessAttempt

        for _ in range(5):
            self.client.post(
                reverse('login'),
                {'username': 'vecino_seg', 'password': 'WrongPassword'},
            )
        self.assertEqual(
            self.client.post(
                reverse('login'),
                {'username': 'vecino_seg', 'password': 'PasswordSegura123!'},
            ).status_code,
            429,
        )

        # Simular el paso de 16 minutos (> 15 min de enfriamiento) sin esperar en tiempo real
        AccessAttempt.objects.update(attempt_time=timezone.now() - timedelta(minutes=16))

        resp_recuperado = self.client.post(
            reverse('login'),
            {'username': 'vecino_seg', 'password': 'PasswordSegura123!'},
        )
        self.assertRedirects(resp_recuperado, reverse('reservas'))
