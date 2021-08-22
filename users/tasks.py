from django.core.mail import send_mail


from netology_diplom.celery import celery_app


@celery_app.task()
def send_email_task(topic, message, sender, receiver, **kwargs):

    send_mail(topic, message, sender, receiver, **kwargs)
