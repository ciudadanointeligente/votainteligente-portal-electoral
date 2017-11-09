from itertools import groupby
from django.forms.models import (
    ModelChoiceIterator, ModelChoiceField, ModelMultipleChoiceField
)


class Grouped(object):
    def __init__(self, queryset, group_by_field,
                 group_label=None, *args, **kwargs):
        """ 
        ``group_by_field`` is the name of a field on the model to use as
                           an optgroup.
        ``group_label`` is a function to return a label for each optgroup.
        """
        super(Grouped, self).__init__(queryset, *args, **kwargs)
        self.group_by_field = group_by_field
        if group_label is None:
            self.group_label = lambda group: group
        else:
            self.group_label = group_label
   
    def _get_choices(self):
        if hasattr(self, '_choices'):
            return self._choices
        return GroupedModelChoiceIterator(self)


class GroupedModelChoiceIterator(ModelChoiceIterator):
    def __iter__(self):
        if self.field.empty_label is not None:
            yield ("", self.field.empty_label)
        queryset = self.queryset.all()
        if not queryset._prefetch_related_lookups:
            queryset = queryset.iterator()
        for group, choices in groupby(self.queryset.all(),
                    key=lambda row: getattr(row, self.field.group_by_field)):
            if self.field.group_label(group):
                yield (
                    self.field.group_label(group),
                    [self.choice(ch) for ch in choices]
                )


class GroupedModelChoiceField(Grouped, ModelChoiceField):
    choices = property(Grouped._get_choices, ModelChoiceField._set_choices)


class GroupedModelMultiChoiceField(Grouped, ModelMultipleChoiceField):
    choices = property(Grouped._get_choices, ModelMultipleChoiceField._set_choices)