from django.db import models
from custom_user.models import CustomUser
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

class Carpeta(models.Model):
    name = models.CharField(max_length=30)
    dueño = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    carpeta_padre = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders')

    def get_descendants(self):
        descendants = [self]
        for subfolder in self.subfolders.all():
            descendants.extend(subfolder.get_descendants())
        return descendants
    
    def __str__(self):
        return self.name

class Archivo(models.Model):
    name = models.CharField(max_length=50)
    archivo = models.FileField(upload_to='files/')
    dueño = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    carpeta_padre = models.ForeignKey(Carpeta, on_delete=models.CASCADE, null=True, blank=True)

    def is_pdf(self):
        try:
            FileExtensionValidator(allowed_extensions=['pdf'])(self)
            return True
        except ValidationError as e:
            return False
    
    def is_image(self):
        try:
            FileExtensionValidator(allowed_extensions=['jpeg','jpg','png'])(self)
            return True
        except ValidationError as e:
            return False
        
    def is_doc(self):
        try:
            FileExtensionValidator(allowed_extensions=['doc','docx','dot','dotx','docm','dotm'])(self)
            return True
        except ValidationError as e:
            return False
        
    def is_excel(self):
        try:
            FileExtensionValidator(allowed_extensions=['xls','xlsx','xlsm','xlsb','xltx','xltm'])(self)
            return True
        except ValidationError as e:
            return False

    def is_ppt(self):
        try:
            FileExtensionValidator(allowed_extensions=['ppt','pptx','pot','potx','pptm','potm'])(self)
            return True
        except ValidationError as e:
            return False
    
    def is_video(self):
        try:
            FileExtensionValidator(allowed_extensions=['mp4','mov','avi','mkv'])(self)
            return True
        except ValidationError as e:
            return False
        
    def str(self):
        return self.name
    
    def clean(self):
        # Si el archivo ya existe, entonces se valida la extensión
        if self.archivo:
            try:
                FileExtensionValidator(allowed_extensions=['pdf','jpeg','jpg','png','doc','docx','dot','dotx','docm','dotm','xls','xlsx','xlsm','xlsb','xltx','xltm','ppt','pptx','pot','potx','pptm','potm','mp4','mov','avi','mkv','txt'])(self.archivo)
            except ValidationError as e:
                raise ValidationError({'archivo': ('Este tipo de archivo no está permitido')}) 
        # Si se está moviendo el archivo y no se selecciona un nuevo archivo, no se realiza ninguna validación
        elif not self.carpeta_padre:
            raise ValidationError({'archivo': ('Debe subir un archivo.')})
        