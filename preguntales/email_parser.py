# coding=utf-8
import re
from preguntales.models import (Answer,
                                Message,
                                OutboundMessage,
                                Attachment
                                )
from elections.models import Candidate

class EmailAnswer(object):
    def __init__(self):
        self.subject = ''
        self._content_text = ''
        self.content_html = ''
        self.answer_identifier = ''
        self.email_from = ''
        self.email_to = ''
        self.when = ''
        self.message_id = None  # http://en.wikipedia.org/wiki/Message-ID
        self.is_bounced = False
        self.attachments = []

    def get_content_text(self):
        cleaned_content = self._content_text
        # pattern = '[\w\.-]+@[\w\.-]+'
        # expression = re.compile(pattern)
        # cleaned_content = re.sub(expression, '', cleaned_content)
        if self.email_to:
            email_to = re.escape(self.email_to)
            expression = re.compile(" ?\n".join(email_to.split()))
            # Joining the parts of the "To" header with a new line
            # So if for example the "To" header comes as follow
            # Felipe Álvarez <giant-email@tremendous-email.org>
            # it would match in the content the following
            # Felipe
            # Álvarez
            # <giant-email@tremendous-email.org>
            # This is to avoid things like the one in #773
            cleaned_content = expression.sub('', cleaned_content)
        cleaned_content = re.sub(r'[\w\.-\.+]+@[\w\.-]+', '', cleaned_content)
        cleaned_content = cleaned_content.replace(self.answer_identifier, '')
        return cleaned_content

    def set_content_text(self, value):
        self._content_text = value

    content_text = property(get_content_text, set_content_text)

    def save(self):
        outboundmessage = OutboundMessage.objects.get(key=self.answer_identifier)
        candidate = Candidate.objects.get(person_ptr=outboundmessage.person)
        answer = Answer.objects.create(message=outboundmessage.message,
                                       content=self.content_text,
                                       person=candidate)
        for attachment in self.attachments:
            Attachment.objects.create(answer=answer,
                                      content=attachment,
                                      name=attachment.name)
        return answer

    def send_back(self):
        if self.is_bounced:
            self.report_bounce()
        else:
            answer = self.save()
            raw_answers = RawIncomingEmail.objects.filter(message_id=self.message_id)
            if answer is not None:
                for attachment in self.attachments:
                    self.save_attachment(answer, attachment)
                if raw_answers:
                    raw_email = raw_answers[0]
                    raw_email = RawIncomingEmail.objects.get(message_id=self.message_id)
                    raw_email.answer = answer
                    raw_email.save()
                return answer

    def add_attachment(self, attachment):
        self.attachments.append(attachment)

