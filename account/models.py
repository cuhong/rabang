from django.db import models

import random
import uuid

from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from rest_framework.authtoken.models import Token

from common.models import DateTimeMixin


class UserManager(BaseUserManager):
    def create_user(self, email, name, cellphone, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            cellphone=cellphone
        )

        user.set_password(password)
        user.save(using=self._db)
        token = Token.objects.create(user=user)
        return user

    def create_superuser(self, email, name, cellphone, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
            cellphone=cellphone
        )
        user.is_superuser = True
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(PermissionsMixin, AbstractBaseUser):
    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)

    id = models.UUIDField(default=uuid.uuid4, null=False, blank=False, unique=True, primary_key=True, editable=False)
    registered_at = models.DateTimeField(auto_now_add=True, verbose_name='가입일자')
    email = models.EmailField(
        verbose_name='이메일',
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=50, null=False, blank=False, verbose_name='이름')
    cellphone = models.CharField(max_length=11, null=False, blank=False, verbose_name='휴대전화')
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'cellphone']

    def __str__(self):
        return "{}({})".format(self.name, self.email)

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def is_seller(self):
        if self.seller:
            return True
        else:
            return False



class UserFkMixin(models.Model):
    class Meta:
        abstract = True

    user = models.ForeignKey(User, null=False, blank=False, verbose_name='사용자', on_delete=models.PROTECT)
