from django.core.validators import validate_email
from django.conf import settings as django_settings

validators = {
    'mail': validate_email
}

area_settings = {
    5:'slug',
    7:'area_name',
    9: 'election_name',
}
candidate_settings = {
    
    10: 'nome_completo',
    12: 'number',
    13: 'cpf',
    14: 'nome',
    25: 'job',
    26: 'date_of_birth',
    30: 'gender',
    32: 'education',
    34: 'civil_status',
    36: 'race',
    45: 'mail',

}
partido_settings = {
    17: 'number',
    19: 'name',
    18: 'initials'
}
coaligacao_settings = {
    23: "name",
    22: "partidos_coaligacao",
    21: "number"

}
_settings = {
    'area': area_settings,
    'candidate': candidate_settings,
    'partido': partido_settings,
    'coaligacao': coaligacao_settings
}


class RowReader(object):
    
    def __init__(self, row, settings):
        self.row = row
        self.settings = settings

    def process(self):
        result = {}
        for key in self.settings.keys():
            entity_definition = self.settings[key]
            temporary_result = {}
            for number in entity_definition:
                entity_key = entity_definition[number]
                try:
                    entity_value = self.row[number]
                except IndexError:
                    print u'Numero no encontrado ' + unicode(number)
                if entity_key in validators:
                    validator = validators[entity_key]
                    try:
                        validator(entity_value)
                    except:
                        entity_value = None
                temporary_result[entity_key] = entity_value
            result[key] = temporary_result
        return result


class MultipleRowsReader(object):
    

    def __init__(self, rows, settings=None):
        self.rows = rows
        self.settings = settings or django_settings.TSE_IMPORTER_CONF or _settings

    def _process(self):
        result = []
        for row in self.rows:
            row_reader = RowReader(row, settings=self.settings)
            row_result = row_reader.process()
            result.append(row_result)
        return result

    def _post_process(self, results):
        existing_emails = {}
        counter = 0
        for row in results:
            email = row['candidate']['mail']
            if email is None:
                results[counter]['email_repeated'] = None
            else:
                if email in existing_emails:
                    results[counter]['email_repeated'] = True
                    existing_emails[email].append(counter)
                    ## Update all previous emails
                    for existing_row_number in existing_emails[email]:
                        results[existing_row_number]['email_repeated'] = True
                else:
                    results[counter]['email_repeated'] = False
                    existing_emails[email] = [counter]
            counter += 1
        return results

    def process(self):
        result = self._process()
        result = self._post_process(result)
        return result

class RowsReaderAdapter(MultipleRowsReader):

    def do_something(self, row):
        raise NotImplementedError

    def process(self):
        results = super(RowsReaderAdapter, self).process()
        for r in results:
            self.do_something(r)
        return results