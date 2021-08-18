from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal

from netology_diplom import settings
from rest_framework.authtoken.models import Token
from django_rest_passwordreset.signals import reset_password_token_created, post_password_reset

from users.models import Account

new_order = Signal(providing_args=['user_id'])
order_confirmation = Signal(providing_args=['user_id'])
products_update = Signal(providing_args=['user_id'])


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_token(instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, **kwargs):

    send_mail(
        f"Password Reset Token for {reset_password_token.user}",
        reset_password_token.key,
        settings.EMAIL_HOST_USER,
        [reset_password_token.user.email],
        fail_silently=False,
    )


@receiver(post_password_reset)
def password_changed(sender, user, **kwargs):

    send_mail(f"Password reset confirmation for {user}",
              'Password has been changed',
              settings.EMAIL_HOST_USER,
              [user.email]
              )


@receiver(new_order)
def new_order_signal(user_id, **kwargs):

    user = Account.objects.get(id=user_id)

    partner_receivers = Account.objects.filter(shop__product_info__ordered_items__order__user=user).distinct()

    partner_emails = [partner.email for partner in partner_receivers]

    send_mail('Оформлен новый заказ',
              'Заказ сформирован',
              settings.EMAIL_HOST_USER,
              partner_emails
              )


@receiver(order_confirmation)
def order_confirmation_signal(user_id, **kwargs):

    user = Account.objects.get(id=user_id)

    send_mail('Подтверждение заказа',
              'Ваш заказ принят',
              settings.EMAIL_HOST_USER,
              [user.email]
              )


@receiver(products_update)
def products_update_signal(user_id, **kwargs):

    user = Account.objects.get(id=user_id)

    send_mail('Обновления прайса',
              f'Пользователь {user} обновил данные о своих товарах',
              settings.EMAIL_HOST_USER,
              [settings.EMAIL_HOST_USER]
              )
