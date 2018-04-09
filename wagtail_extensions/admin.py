from django.db.models.expressions import RawSQL
from django.contrib import admin as django_admin

from .jsonfield_utils import jsonfield_path_split


def jsonfield_simplelistfilter_builder(field_path, parameter_name, title=None):
    """
    Function to build and return a standard Django `SimpleListFilter` class
    specific to a given field path nested within a `JSONField` to make it
    available for filtering by distinct values in the admin.
    """
    class _Filter(django_admin.SimpleListFilter):

        def lookups(self, request, model_admin):
            """ Find all distinct values for a field path in a `JSONField` """
            # Split a standard Django dunder field path into an SQL statement
            # that will work with a PostgreSQL JSONB SQL syntax, for example
            # "data__a__b" => "'data' #>> {'a','b'}"
            jsonb_field_name, json_path = jsonfield_path_split(field_path)
            sql_field_path = '{%s}' % ','.join(json_path)

            # TODO A Django version > 2.0 may remove the need for these
            # contortions: https://code.djangoproject.com/ticket/24747
            qs = model_admin.model.objects \
                .filter(**{'%s__isnull' % field_path: False}) \
                .annotate(
                    field_data=RawSQL(
                        jsonb_field_name + " #>> %s",
                        (sql_field_path,),
                    )
                ) \
                .values_list('field_data', flat=True) \
                .order_by('field_data') \
                .distinct()
            return [(i, i) for i in qs]

        def queryset(self, request, queryset):
            """ Filter by a selected known value for a field path """
            if self.value():
                kwargs = {field_path: self.value()}
                return queryset.filter(**kwargs)
            return queryset

    _Filter.parameter_name = parameter_name
    _Filter.title = title or parameter_name

    return _Filter
