from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from drive.models import Archivo, Carpeta
from custom_user.models import CustomUser
from django.core.exceptions import ValidationError

class SubirYEliminarArchivoTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(email='prueba@example.com', password='useruser')
        self.archivo = Archivo.objects.create(name='Archivo Test.txt', archivo='files/archivo_test.txt', dueño=self.user, carpeta_padre=None)
        self.client = Client()
        self.client.force_login(self.user)

    #Unitario
    def test_modelo_archivo(self):
        archivo = Archivo.objects.create(name='Archivo Test.txt', archivo='files/archivo_test.txt', dueño=self.user, carpeta_padre=None)
        self.assertEqual(archivo.name, 'Archivo Test.txt')
        self.assertEqual(archivo.archivo, 'files/archivo_test.txt')

    #Unitario
    def test_modelo_carpeta(self):
        carpeta = Carpeta.objects.create(nombre='Carpeta Nombre', dueño=self.user, carpeta_padre=None)
        self.assertEqual(carpeta.nombre, 'Carpeta Nombre')

    #Unitario
    def test_nombre_max_length(self):
        archivo = Archivo(name='a' * 101, archivo='files/archivo_test.txt', dueño=self.user, carpeta_padre=None)
        with self.assertRaises(ValidationError):
            archivo.full_clean()

    #Unitario
    def test_archivo_extension_valida(self):
        uploaded = SimpleUploadedFile('test_file.exe', b"contenido de prueba")
        archivo = Archivo(name='Archivo Test.txt', archivo=uploaded, dueño=self.user, carpeta_padre=None)
        
        with self.assertRaises(ValidationError):
            archivo.full_clean()
    
    def test_subir_archivo(self):
        carpeta = Carpeta.objects.create(nombre='Carpeta de prueba', dueño=self.user)
        archivo = SimpleUploadedFile("archivo.txt", b"contenido de prueba")

        data = {
            'archivo': archivo,
            'carpeta_actual': carpeta.id
        }
        response = self.client.post(reverse('subir_archivo'), data)
        self.assertEqual(response.status_code, 200)

        self.assertTrue(Archivo.objects.filter(name='archivo.txt',carpeta_padre=carpeta).exists())

    def test_subir_archivo_invalido(self):
        archivo = SimpleUploadedFile("archivo.exe", b"contenido de prueba")

        data = {
            'archivo': archivo
        }
        response = self.client.post(reverse('subir_archivo'), data)
        self.assertEqual(response.status_code, 400)

        self.assertFalse(Archivo.objects.filter(name='archivo.exe').exists())

    def test_eliminar_archivo(self):
        response = self.client.get('/drive/eliminar/'+str(self.archivo.id))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Archivo.objects.filter(name='Archivo Test.txt').exists())

class ListarArchivosTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(email='prueba@example.com', password='useruser')
        self.client = Client()
        self.client.force_login(self.user)
        
        self.carpeta_raiz = Carpeta.objects.create(nombre='Carpeta Raiz', dueño=self.user)
        self.carpeta_sub = Carpeta.objects.create(nombre='Carpeta Sub', dueño=self.user, carpeta_padre=self.carpeta_raiz)
        self.archivo_raiz = Archivo.objects.create(name='Archivo Raiz.txt', archivo='files/archivo_raiz.txt', dueño=self.user, carpeta_padre=None)
        self.archivo_sub = Archivo.objects.create(name='Archivo Sub.txt', archivo='files/archivo_sub.txt', dueño=self.user, carpeta_padre=self.carpeta_raiz)
    
    def test_listar_archivos_raiz(self):
        response = self.client.get(reverse('listar_archivos'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Archivo Raiz.txt')
        self.assertContains(response, 'Carpeta Raiz')
    
    def test_listar_archivos_subcarpeta(self):
        response = self.client.get('/drive/listar/'+str(self.carpeta_raiz.id))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'Archivo Sub.txt')
        self.assertContains(response, 'Carpeta Sub')

    def test_listar_archivos_carpeta_inexistente(self):
        response = self.client.get('/drive/listar/9999')
        self.assertEqual(response.status_code, 404)

class MoverArchivoTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create(email='prueba@example.com', password='useruser')
        self.carpeta = Carpeta.objects.create(nombre='testfolder', dueño=self.user)
        self.archivo = Archivo.objects.create(name='Archivo Test.txt', archivo='files/archivo_test.txt',dueño=self.user, carpeta_padre=self.carpeta)
                
        self.client.force_login(self.user)

    def test_mover_archivo(self):
        new_folder = Carpeta.objects.create(nombre='Folder 2', dueño=self.user)
        response = self.client.post(reverse('mover_archivo', args=[self.archivo.id]), {'carpeta_padre': new_folder.id})
        self.archivo.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.archivo.carpeta_padre, new_folder)

    def test_obtener_carpetas_destino_carpeta(self):
        carpeta2= Carpeta.objects.create(nombre='testfolder2', dueño=self.user, carpeta_padre=None)
        response = self.client.get(reverse('obtener_carpetas_destino', args=[self.carpeta.id]))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {"available_folders": [{"id": carpeta2.id, "nombre": carpeta2.nombre}]}
        )
