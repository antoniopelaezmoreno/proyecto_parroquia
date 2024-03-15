from django.db import models
from custom_user.models import CustomUser
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

class File(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='files/')
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

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
        