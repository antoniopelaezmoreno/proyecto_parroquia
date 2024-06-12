from django.test import TestCase, Client, RequestFactory
from catecumeno.models import Catecumeno
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from custom_user.models import CustomUser
from grupo.models import Grupo
import json
from catecumeno.views import crear_catecumeno, listar_catecumenos, editar_catecumeno
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError

# Create your tests here.

class CrearCatecumenoTestCase(TestCase):

    def setUp(self):
        self.datos_invalidos = {
            'nombre': 'nombre',
            'apellidos': 'apellidos'
        }
        self.datos = {
            'nombre': 'nombre',
            'apellidos': 'apellidos',
            'email':'email@gmail.com',
            'dni':'12345678A',
            'telefono':'123456789',
            'ciclo': Catecumeno.CicloChoices.POSCO_1,
            'nombre_madre':'Nombre Madre',
            'apellidos_madre':'Apellidos Madre',
            'email_madre':'emailmadre@gmail.com',
            'telefono_madre':'123456789',
            'nombre_padre':'Nombre Padre',
            'apellidos_padre':'Apellidos Padre',
            'email_padre':'emailpadre@gmail.com',
            'telefono_padre':'123456789',
            'preferencias':'Preferencias'
        }
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
        )
        self.uploaded = SimpleUploadedFile('small.jpg', small_gif, content_type='image/jpg')
        self.datos['foto'] = self.uploaded
    
    def _add_session_to_request(self, request):
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

    #Unitario
    def test_modelo_catecumeno(self):
        catecumeno = Catecumeno.objects.create(**self.datos)
        self.assertEqual(catecumeno.nombre, 'nombre')
        self.assertEqual(catecumeno.apellidos, 'apellidos')

    #Unitario
    def test_nombre_max_length(self):
        catecumeno = Catecumeno(nombre='a' * 101, apellidos='Apellidos', email='email@gmail.com', dni='12345678A', telefono='123456789', ciclo=Catecumeno.CicloChoices.POSCO_1)
        with self.assertRaises(ValidationError):
            catecumeno.full_clean()

    #Unitario
    def test_validacion_telefono(self):
        catecumeno = Catecumeno(nombre='Nombre', apellidos='Apellidos', email='email@gmail.com', dni='12345678A', telefono='1234567890', ciclo=Catecumeno.CicloChoices.POSCO_1)
        with self.assertRaises(ValidationError):
            catecumeno.full_clean()

    #Unitario
    def test_validacion_dni(self):
        catecumeno = Catecumeno(nombre='Nombre', apellidos='Apellidos', email='email@gmail.com', dni='12345678', telefono='123456789', ciclo=Catecumeno.CicloChoices.POSCO_1)
        with self.assertRaises(ValidationError):
            catecumeno.full_clean()

    #Unitario
    def test_foto_extension_valida(self):
        uploaded = SimpleUploadedFile('test_image.exe', b"contenido de prueba")
        
        catecumeno = Catecumeno(nombre='Nombre', apellidos='Apellidos', email='email@gmail.com', dni='12345678A', telefono='123456789', ciclo=Catecumeno.CicloChoices.POSCO_1, foto=uploaded)
        
        with self.assertRaises(ValidationError):
            catecumeno.full_clean()

    #Unitario
    def test_vista_crear_catecumeno(self):
        request = RequestFactory().post(reverse('crear_catecumeno'), self.datos)
        request.user = CustomUser.objects.create_user(email='testuser@example.com', password='testuser123')
        self._add_session_to_request(request)
        self.client.force_login(request.user)
        response = crear_catecumeno(request)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        self.assertTrue(json.loads(response.content.decode('utf-8')).get('success'))

    #Unitario
    def test_vista_crear_catecumeno_datos_vacios(self):

        request = RequestFactory().post(reverse('crear_catecumeno'), self.datos_invalidos)
        request.user = CustomUser.objects.create_user(email='testuser@example.com', password='testuser123')
        self._add_session_to_request(request)
        self.client.force_login(request.user)
        response = crear_catecumeno(request)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        self.assertFalse(json.loads(response.content.decode('utf-8')).get('success'))

    #Integración
    def test_crear_catecumeno(self):
        datos = {

            'nombre': 'nombre',
            'apellidos': 'apellidos',
            'email':'email@gmail.com',
            'dni':'12345678A',
            'telefono':'123456789',
            'ciclo': Catecumeno.CicloChoices.POSCO_1,
            'nombre_madre':'Nombre Madre',
            'apellidos_madre':'Apellidos Madre',
            'email_madre':'emailmadre@gmail.com',
            'telefono_madre':'123456789',
            'nombre_padre':'Nombre Padre',
            'apellidos_padre':'Apellidos Padre',
            'email_padre':'emailpadre@gmail.com',
            'telefono_padre':'123456789',
            'preferencias':'Preferencias'
        }
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile('small.jpg', small_gif, content_type='image/jpg')
        datos['foto'] = uploaded
        response = self.client.post(reverse('crear_catecumeno'), datos)
        
        self.assertEqual(response.status_code, 200)
        
        catecumeno =Catecumeno.objects.last()
        self.assertEqual(catecumeno.nombre, 'nombre')
        self.assertEqual(catecumeno.apellidos, 'apellidos')

    def test_crear_catecumeno_campos_vacios(self):
        datos = {
            'nombre': 'nombre',
            'apellidos': 'apellidos',
        }
        response = self.client.post(reverse('crear_catecumeno'), datos)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Catecumeno.objects.exists())

    def test_crear_catecumeno_campos_invalidos(self):
        datos = {
            'nombre': 'nombre',
            'apellidos': 'apellidos',
            'email':'email@gmail.com',
            'dni':'12345678A',
            'telefono':'123456789',
            'ciclo': Catecumeno.CicloChoices.POSCO_1,
            'nombre_madre':'Nombre Madre',
            'apellidos_madre':'Apellidos Madre',
            'email_madre':'emailmadre@gmail.com',
            'telefono_madre':'123456789',
            'nombre_padre':'Nombre Padre',
            'apellidos_padre':'Apellidos Padre',
            'email_padre':'emailpadre@gmail.com',
            'telefono_padre':'123456789',
            'preferencias':'Preferencias'
        }
        response = self.client.post(reverse('crear_catecumeno'), datos)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Catecumeno.objects.exists())

class ListarCatecumenosTestCase(TestCase):

    def setUp(self):
        # Crear usuarios para simular diferentes roles y ciclos
        self.superuser = CustomUser.objects.create_superuser(email='admin@gmail.com', password='admin123')
        self.coord = CustomUser.objects.create_user(email='coord@gmail.com', password='coord123')
        self.coord.is_coord = True
        self.coord.ciclo = Catecumeno.CicloChoices.POSCO_1
        self.coord.save()
        self.catequista = CustomUser.objects.create_user(email='catequista@gmail.com', password='catequista123')

    #Unitario
    def test_listar_catecumenos(self):
        request = RequestFactory().get(reverse('listar_catecumenos'))
        request.user = self.superuser
        response = listar_catecumenos(request)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, HttpResponse)

    #Unitario
    def test_listar_catecumenos_usuario_no_autenticado(self):
        request = RequestFactory().get(reverse('listar_catecumenos'))
        request.user = AnonymousUser()
        response = listar_catecumenos(request)
        self.assertEqual(response.status_code, 302)
    
    #Integración
    def test_listar_catecumenos_superuser(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse('listar_catecumenos'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'listar_catecumenos_admin.html')

    def test_listar_catecumenos_coordinador(self):
        self.client.force_login(self.coord)
        response = self.client.get(reverse('listar_catecumenos'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'listar_catecumenos.html')

    def test_listar_catecumenos_catequista(self):
        self.client.force_login(self.catequista)
        response = self.client.get(reverse('listar_catecumenos'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'listar_catecumenos.html')

    def test_listar_catecumenos_sin_permisos(self):
        response = self.client.get(reverse('listar_catecumenos'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/user/login?next=/catecumeno/listar/')

class EditarCatecumenoTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.superuser = CustomUser.objects.create_superuser(email='admin@gmail.com', password='admin123')
        self.coord = CustomUser.objects.create_user(email='coord@gmail.com', password='coord123')
        self.coord.is_coord = True
        self.coord.ciclo = Catecumeno.CicloChoices.POSCO_1
        self.coord.save()
        self.catequista = CustomUser.objects.create_user(email='catequista@gmail.com', password='catequista123')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile('small.jpg', small_gif, content_type='image/jpg')
        self.data = {
            'nombre': 'Nombre Modificado',
            'apellidos': 'Apellidos Modificados',
            'email':'email@gmail.com',
            'dni':'12345678A',
            'telefono':'123456789',
            'ciclo': Catecumeno.CicloChoices.POSCO_1,
            'nombre_madre':'Nombre Madre',
            'apellidos_madre':'Apellidos Madre',
            'email_madre':'emailmadre@gmail.com',
            'telefono_madre':'123456789',
            'nombre_padre':'Nombre Padre',
            'apellidos_padre':'Apellidos Padre',
            'email_padre':'emailpadre@gmail.com',
            'telefono_padre':'123456789',
            'preferencias':'Preferencias',
            'foto': uploaded
        }

    def test_editar_catecumeno_superusuario(self):
        self.client.force_login(self.superuser)
        catecumeno = Catecumeno.objects.create(nombre='Nombre', apellidos='Apellidos', email='email@gmail.com', dni='12345678A', telefono='123456789', ciclo=Catecumeno.CicloChoices.POSCO_1)        
        response = self.client.post(reverse('editar_catecumeno', args=[catecumeno.id]), self.data)
        self.assertEqual(response.status_code, 302)
        catecumeno.refresh_from_db()
        self.assertEqual(catecumeno.nombre, 'Nombre Modificado')
        self.assertEqual(catecumeno.apellidos, 'Apellidos Modificados')
    
    def test_editar_catecumeno_coordinador_autorizado(self):
        self.client.force_login(self.coord)
        catecumeno = Catecumeno.objects.create(nombre='Nombre', apellidos='Apellidos', email='email@gmail.com', dni='12345678A', telefono='123456789', ciclo=Catecumeno.CicloChoices.POSCO_1)
        response = self.client.post(reverse('editar_catecumeno', args=[catecumeno.id]), self.data)
        self.assertEqual(response.status_code, 302)
        catecumeno.refresh_from_db()
        self.assertEqual(catecumeno.nombre, 'Nombre Modificado')
        self.assertEqual(catecumeno.apellidos, 'Apellidos Modificados')
        
    def test_editar_catecumeno_coordinador_no_autorizado(self):
        self.client.force_login(self.coord)
        catecumeno = Catecumeno.objects.create(nombre='Nombre', apellidos='Apellidos', email='email@gmail.com', dni='12345678A', telefono='123456789', ciclo=Catecumeno.CicloChoices.POSCO_2)  
        response = self.client.get(reverse('editar_catecumeno', args=[catecumeno.id]))
        self.assertEqual(response.status_code, 302) 

    def test_editar_catecumeno_catequista_no_autorizado(self):
        self.client.force_login(self.catequista)
        catecumeno = Catecumeno.objects.create(nombre='Nombre', apellidos='Apellidos', email='email@gmail.com', dni='12345678A', telefono='123456789', ciclo=Catecumeno.CicloChoices.POSCO_1)
        response = self.client.get(reverse('editar_catecumeno', args=[catecumeno.id]))
        self.assertEqual(response.status_code, 302)

class AsignarCatecumenosAGrupoTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.superuser = CustomUser.objects.create_superuser(email='admin@example.com', password='admin123')
        self.coord = CustomUser.objects.create_user(email='coord@example.com', password='coord123')
        self.coord.is_coord = True
        self.coord.ciclo = Catecumeno.CicloChoices.POSCO_1
        self.coord.save()
        self.catecumeno = Catecumeno.objects.create(nombre='Nombre', apellidos='Apellidos', email='email@gmail.com', dni='12345678A', telefono='123456789', ciclo=Catecumeno.CicloChoices.POSCO_1)
        self.catequista1 = CustomUser.objects.create_user(email='catequista1@example.com', password='catequista123')
        self.catequista2 = CustomUser.objects.create_user(email='catequista2@example.com', password='catequista123')
        self.grupo = Grupo.objects.create(catequista1=self.catequista1, catequista2=self.catequista2, ciclo=Catecumeno.CicloChoices.POSCO_1)

    def test_asignar_catecumenos_a_grupo_post(self):
        self.client.force_login(self.coord)
        data = [{'userId': self.catecumeno.id, 'grupoAsignado': self.grupo.id}]
        response = self.client.post(reverse('asignar_catecumenos_a_grupo'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 302) 

        catecumeno_actualizado = Catecumeno.objects.get(id=self.catecumeno.id)
        self.assertEqual(catecumeno_actualizado.grupo, self.grupo)

    def test_asignar_catecumenos_a_grupo_no_autorizado(self):
        self.client.force_login(self.catequista1)
        response = self.client.get(reverse('asignar_catecumenos_a_grupo'))
        self.assertEqual(response.status_code, 302)
