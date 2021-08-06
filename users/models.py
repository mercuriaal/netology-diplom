from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


USER_TYPE_CHOICES = (
    ('partner', 'Поставщик'),
    ('client', 'Покупатель'),

)


class Account(AbstractUser):

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'

    username_validator = UnicodeUsernameValidator()

    email = models.EmailField(unique=True)
    company = models.CharField(verbose_name='Компания', max_length=40, blank=True)
    position = models.CharField(verbose_name='Должность', max_length=40, blank=True)
    type = models.CharField(verbose_name='Тип пользователя', choices=USER_TYPE_CHOICES, max_length=10, default='client')
    username = models.CharField(
        ('username'),
        max_length=150,
        help_text=('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': ("A user with that username already exists."),
        },
    )

    def __str__(self):
        return f'{self.email}'

    class Meta(AbstractUser.Meta):
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Список пользователей'
        ordering = ('email',)
        swappable = 'AUTH_USER_MODEL'


class Contact(models.Model):
    user = models.ForeignKey(Account, verbose_name='Пользователь',
                             related_name='contacts',
                             on_delete=models.CASCADE)

    city = models.CharField(max_length=50, verbose_name='Город')
    street = models.CharField(max_length=100, verbose_name='Улица')
    house = models.CharField(max_length=15, verbose_name='Дом', blank=True)
    structure = models.CharField(max_length=15, verbose_name='Корпус', blank=True)
    building = models.CharField(max_length=15, verbose_name='Строение', blank=True)
    apartment = models.CharField(max_length=15, verbose_name='Квартира', blank=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон')

    class Meta:
        verbose_name = 'Контакты пользователя'
        verbose_name_plural = 'Список контактов пользователя'

    def __str__(self):
        return f'г.{self.city}, ул.{self.street}, тел.{self.phone}'


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_token(instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)