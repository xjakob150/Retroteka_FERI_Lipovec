from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db import models
from django.db.models.functions import Lower


class UserManager(DjangoUserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields['role'] = User.Role.ADMIN
        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        COLLECTOR = 'collector', 'Collector'
        MODERATOR = 'moderator', 'Moderator'
        ADMIN = 'admin', 'Administrator'

    email = models.EmailField()
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.COLLECTOR)

    objects = UserManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(Lower('username'), name='unique_username_ignore_case'),
            models.UniqueConstraint(Lower('email'), name='unique_email_ignore_case'),
        ]

    def save(self, *args, **kwargs):
        self.is_staff = self.role == self.Role.ADMIN
        update_fields = kwargs.get('update_fields')
        if update_fields is not None and 'role' in update_fields:
            kwargs['update_fields'] = {*update_fields, 'is_staff'}
        super().save(*args, **kwargs)
