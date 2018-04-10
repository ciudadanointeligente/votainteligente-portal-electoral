# coding=utf-8
from django.test import TestCase
from django.template import Template, Context
from django.template.loader import get_template

class TemplateTagsTestCase(TestCase):
    def setUp(self):
        super(TemplateTagsTestCase, self).setUp()

    def test_mail_signature_html(self):
        template = Template("{% load votainteligente_extras %}{% mail_signature_html %}")
        context = Context({})
        expected_template = get_template('mails/signature.html').render({})

        self.assertEqual(template.render(context), expected_template)

    def test_mail_signature_txt(self):
        template = Template("{% load votainteligente_extras %}{% mail_signature_txt %}")
        context = Context({})
        expected_template = get_template('mails/signature.txt').render({})

        self.assertEqual(template.render(context), expected_template)
