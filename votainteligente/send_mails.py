# coding=utf-8
from django.template.loader import get_template
from django.core.mail import EmailMessage
from django.template import Context
from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


def validateEmail(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def send_mail(context_dict, template_prefix, to=[], reply_to=None, from_email=settings.DEFAULT_FROM_EMAIL):
    validated_to = []
    for m in to:
        if validateEmail(m):
            validated_to.append(m)
    to = validated_to
    context = Context(context_dict)
    template_prefix_dict = {'template_prefix': template_prefix}
    template_body = get_template('mails/%(template_prefix)s_body.html' % template_prefix_dict)
    body = template_body.render(context)
    template_subject = get_template('mails/%(template_prefix)s_subject.html' % template_prefix_dict)
    subject = template_subject.render(context).replace('\n', '').replace('\r', '')
    email = EmailMessage(subject, body, from_email, to)
    if reply_to is not None:
        email.reply_to = [reply_to]
    email.send()


def send_mails_to_staff(context_dict, template_prefix):
    to = []
    for u in User.objects.filter(is_staff=True):
        to.append(u.email)
    send_mail(context_dict, template_prefix, to=to)

