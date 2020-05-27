from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('email address', unique=True)
    is_staff = models.BooleanField(
        'staff status',
        default=False,
        help_text='Designates whether the user can log into this admin site.',
    )
    is_active = models.BooleanField(
        'active',
        default=True,
        help_text=('Designates whether this user should be treated as active.'
                   'Unselect this instead of deleting accounts.'),
    )

    invitation_code = models.ForeignKey('Code', on_delete=models.PROTECT,
                                        null=True, blank=True,
                                        related_name="invited_list",
                                        verbose_name="joined using code")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
