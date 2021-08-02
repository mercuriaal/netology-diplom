from django.db import models

from django.contrib.auth.models import AbstractUser

USER_TYPE_CHOICES = (
    ('partner', 'Поставщик'),
    ('client', 'Покупатель'),

)


class User(AbstractUser):

    company = models.CharField(verbose_name='Компания', max_length=40, blank=True)
    position = models.CharField(verbose_name='Должность', max_length=40, blank=True)
    type = models.CharField(verbose_name='Тип пользователя', choices=USER_TYPE_CHOICES, max_length=7, default='client')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta(AbstractUser.Meta):
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Список пользователей'
        ordering = ('email',)
        swappable = 'AUTH_USER_MODEL'
