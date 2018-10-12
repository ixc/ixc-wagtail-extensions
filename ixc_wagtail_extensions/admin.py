from django.db.models.expressions import RawSQL
from django.contrib import admin as django_admin

from .jsonfield_utils import jsonfield_path_split


def jsonfield_simplelistfilter_builder(
    field_path, parameter_name, title=None, value_type=None,
):
    """
    Function to build and return a standard Django `SimpleListFilter` class
    specific to a given field path nested within a `JSONField` to make it
    available for filtering by distinct values in the admin.
    """
    supported_value_types = (None, bool)
    if value_type not in supported_value_types:
        raise ValueError(
            "The 'value_type' %r is not supported, only %s"
            % (value_type, supported_value_types))

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
            # Value is always a string at this point
            value = self.value()
            if not value:
                return queryset
            # Convert value to appropriate type
            if value_type is bool:
                value = value.lower() == 'true'
            return queryset.filter(**{field_path: value})

    _Filter.parameter_name = parameter_name
    _Filter.title = title or parameter_name

    return _Filter
