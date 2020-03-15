from .celery import app
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import translation

@app.task
def send_mail_delay(template_path: str, from_mail: str, emails: list, topic: str, text: str, context: dict):

    # translation.activate(language)
    email_html = render_to_string(template_path, context=context)

    number_success_emails = send_mail(
        topic,
        text,
        from_mail,
        emails,
        html_message=email_html,
        fail_silently=False
    )

    return number_success_emails