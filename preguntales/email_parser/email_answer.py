# coding=utf-8
import re
from preguntales.models import (Answer,
                                Message,
                                OutboundMessage,
                                Attachment
                                )
from elections.models import Candidate
from .froide_email_utils import FroideEmailParser
import email
from email_reply_parser import EmailReplyParser
from flufl.bounce import all_failures, scan_message
import logging

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

class EmailHandler(FroideEmailParser):
    def __init__(self, answer_class=EmailAnswer):
        self.message = None
        self.content_types_attrs = {
            'text/plain': 'content_text',
            'text/html': 'content_html',
        }

    def instanciate_answer(self, lines):
        answer = EmailAnswer()
        msgtxt = ''.join(lines)

        msg = email.message_from_string(msgtxt)
        temporary, permanent = all_failures(msg)

        if temporary or permanent:
            answer.is_bounced = True
            answer.email_from = scan_message(msg).pop()
        else:
            answer.email_from = msg["From"]

        the_recipient = msg["To"]
        answer.subject = msg["Subject"]
        answer.when = msg["Date"]
        answer.message_id = msg["Message-ID"]

        the_recipient = re.sub(r"\n", "", the_recipient)

        regex = re.compile(r".*[\+\-](.*)@.*")
        the_match = regex.match(the_recipient)
        if the_match is None:
            raise CouldNotFindIdentifier
        answer.email_to = the_recipient
        answer.answer_identifier = the_match.groups()[0]
        logging.info("Reading the parts")
        for part in msg.walk():
            logging.info("Part of type " + part.get_content_type())

            content_type_attr = self.content_types_attrs.get(part.get_content_type())
            if content_type_attr:
                charset = part.get_content_charset() or "ISO-8859-1"
                data = part.get_payload(decode=True).decode(charset)

                setattr(
                    answer,
                    content_type_attr,
                    EmailReplyParser.parse_reply(data).strip(),
                    )
            else:
                self.handle_not_processed_part(part)

            attachment = self.parse_attachment(part)
            if attachment:
                answer.add_attachment(attachment)

        log = 'New incoming email from %(from)s sent on %(date)s with subject %(subject)s and content %(content)s'
        log = log % {
            'from': answer.email_from,
            'date': answer.when,
            'subject': answer.subject,
            'content': answer.content_text,
            }
        logging.info(log)
        return answer

    def handle_not_processed_part(self, part):
        pass

    def handle(self, lines):
        email_answer = self.instanciate_answer(lines)

        return email_answer

