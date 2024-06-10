from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from catecumeno.models import Catecumeno
from django.core.validators import RegexValidator
from cryptography.fernet import Fernet
import os


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    telefono = models.CharField(
        max_length=9,
        validators=[
            RegexValidator(
                regex='^\d{9}$',
                message='El teléfono debe tener 9 dígitos',
                code='invalid_phone_number'
            )
        ]
    )
    is_coord = models.BooleanField(default=False)
    ciclo = models.CharField(max_length=20, choices=Catecumeno.CicloChoices.choices, default=Catecumeno.CicloChoices.POSCO_1)
    nombre = models.CharField(max_length=30, blank=True)
    apellidos = models.CharField(max_length=150, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    token_json_encrypted = models.BinaryField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.nombre + ' ' + self.apellidos

    def get_by_natural_key(self, email):
        return self.get(email=email)
    
    def encrypt_token(self, token):
        GOOGLE_SECRET_KEY = os.environ.get('GOOGLE_SECRET_KEY')
        encodado = GOOGLE_SECRET_KEY.encode()
        cipher_suite = Fernet(encodado)
        encrypted_token = cipher_suite.encrypt(token.encode())
        self.token_json_encrypted = encrypted_token
        self.save()

    def decrypt_token(self):
        if self.token_json_encrypted:
            token_bytes = bytes(self.token_json_encrypted)
            GOOGLE_SECRET_KEY = os.environ.get('GOOGLE_SECRET_KEY')
            encodado = GOOGLE_SECRET_KEY.encode()
            cipher_suite = Fernet(encodado)
            decrypted_token = cipher_suite.decrypt(token_bytes)
            return decrypted_token.decode()
        else:
            return None
