import os


__testing_mails__ = os.path.dirname(os.path.abspath(__file__)) + '/testing_mails/'
__attachrments_dir__ = __testing_mails__ + 'attachments/'

def read_lines(file_name):
    f = open(file_name)
    lines = f.readlines()
    f.close()
    return lines

def read_mail(mail):
    return read_lines(__testing_mails__ + mail + '.txt')
