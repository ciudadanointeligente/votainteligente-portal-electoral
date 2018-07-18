import unicodecsv as csv


class CsvReader(object):
    def __init__(self, filename):
        self.filename = filename
        file_ = open(self.filename, 'rb')
        reader = csv.reader(file_, encoding='iso-8859-1', delimiter=';')
        self.rows = []
        for row in reader:
            self.rows.append(row)
