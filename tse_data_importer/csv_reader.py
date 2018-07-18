import unicodecsv as csv
from tse_data_importer.importer import RowsReaderAdapter


class CsvReader(RowsReaderAdapter):
    def __init__(self, filename, *args, **kwargs):
        self.filename = filename
        file_ = open(self.filename, 'rb')
        reader = csv.reader(file_, encoding='iso-8859-1', delimiter=';')
        self.rows = []
        for row in reader:
            self.rows.append(row)
        super(CsvReader, self).__init__(self.rows, **kwargs)
