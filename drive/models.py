from django.db import models
from custom_user.models import CustomUser
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

class Folder(models.Model):
    name = models.CharField(max_length=30)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    files = models.ManyToManyField('File', related_name='folders')
    parent_folder = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

class File(models.Model):
    name = models.CharField(max_length=50)
    file = models.FileField(upload_to='files/')
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    parent_folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, blank=True)

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
        if self.file:
            try:
                FileExtensionValidator(allowed_extensions=['pdf','jpeg','jpg','png','doc','docx','dot','dotx','docm','dotm','xls','xlsx','xlsm','xlsb','xltx','xltm','ppt','pptx','pot','potx','pptm','potm','mp4','mov','avi','mkv','txt'])(self.file)
            except ValidationError as e:
                raise ValidationError({'file': ('Este tipo de archivo no está permitido')}) 
        else:
            raise ValidationError({'file': ('Debe subir un archivo.')})
        