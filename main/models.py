from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
import os

from .managers import CustomUserManager

TMP_DIRS = {
    'avatar': os.path.join('tmp', 'avatars'),
    'plates': os.path.join('tmp', 'plates'),
}


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


class Profile(models.Model):
    class Gender(models.IntegerChoices):
        MALE = 1, 'Male'
        FEMALE = 2, 'Female'
        OTHER = 3, 'Other'

    class Templates(models.IntegerChoices):
        SQUARE = 1, 'Square'
        BRICKS = 2, 'Bricks'
        LADDER = 3, 'Ladder'
        JOURNAL = 4, 'Journal'
    owner = models.OneToOneField("CustomUser", on_delete=models.CASCADE)

    first_name = models.CharField('first name', max_length=30, blank=True)
    last_name = models.CharField('last name', max_length=150, blank=True)
    gender = models.IntegerField('gender', choices=Gender.choices, default=Gender.OTHER)
    avatar = models.ImageField('photo', upload_to=TMP_DIRS['avatar'], blank=True)
    date_joined = models.DateTimeField('date joined', default=timezone.now)

    plate_img_1 = models.ImageField('first image', upload_to=TMP_DIRS['plates'], blank=True)
    plate_img_2 = models.ImageField('second image', upload_to=TMP_DIRS['plates'], blank=True)
    plate_img_3 = models.ImageField('third image', upload_to=TMP_DIRS['plates'], blank=True)
    plate_img_4 = models.ImageField('fourth image', upload_to=TMP_DIRS['plates'], blank=True)

    template = models.IntegerField('profile template', choices=Templates.choices, default=Templates.SQUARE)

    finished = models.BooleanField('registration finished', default=False)

    def __str__(self):
        return f'{self.owner.email}\'s profile'


class Code(models.Model):
    class Sorts(models.IntegerChoices):
        PERSONAL = 1, 'Personal'
        ENTERPRISE = 2, 'Enterprise'
        HOST = 3, 'Self-Hosted'

    owner = models.OneToOneField("CustomUser", on_delete=models.PROTECT, related_name="invite_code", null=True)

    number = models.CharField('encoded numeric part', max_length=6)
    sort = models.IntegerField('code type', choices=Sorts.choices)

    code = models.CharField('invitation code', max_length=8)
    url = models.CharField('invitation link', max_length=150)
    qr = models.FileField('invitation qr code', upload_to='qr_codes')

    joined = models.IntegerField('number of invited people', default=0)

    def __str__(self):
        try:
            return f'{self.owner.email}\'s {self.code} code'
        except AttributeError:
            return f'{self.code} {self.get_sort_display()}'