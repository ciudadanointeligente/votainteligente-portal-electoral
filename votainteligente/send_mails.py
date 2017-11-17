# coding=utf-8
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.sites.models import Site
from django.template.exceptions import TemplateDoesNotExist


def validateEmail(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def send_mail(context,
              template_prefix,
              to=[],
              reply_to=None,
              subject=None,
              from_email=settings.DEFAULT_FROM_EMAIL):
    validated_to = []
    for m in to:
        if validateEmail(m):
            validated_to.append(m)
    to = validated_to
    if 'site' not in context.keys():
        context['site'] = Site.objects.get_current()
    template_prefix_dict = {'template_prefix': template_prefix}
    template_body = get_template('mails/%(template_prefix)s/body.txt' % template_prefix_dict)
    body = template_body.render(context)
    template_subject = get_template('mails/%(template_prefix)s/subject.txt' % template_prefix_dict)
    subject = subject or template_subject.render(context).replace('\n', '').replace('\r', '')
    email = EmailMultiAlternatives(subject, body, from_email, to)
    try:
        template_body_html = get_template('mails/%(template_prefix)s/body.html' % template_prefix_dict)
        html_content = template_body_html.render(context)
        email.attach_alternative(html_content, "text/html")
    except TemplateDoesNotExist:
        pass
    if reply_to is not None:
        email.reply_to = [reply_to]
    email.send()


def send_mails_to_staff(context_dict, template_prefix):
    to = []
    for u in User.objects.filter(is_staff=True):
        to.append(u.email)
    send_mail(context_dict, template_prefix, to=to)
