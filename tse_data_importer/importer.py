from django.core.validators import validate_email

validators = {
    'mail': validate_email
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
                entity_value = self.row[number]
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
    def __init__(self, rows, settings):
        self.rows = rows
        self.settings = settings

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
        # raise NotImplementedError
        pass

    def process(self):
        results = super(RowsReaderAdapter, self).process()
        for r in results:
            self.do_something(r)
        return results