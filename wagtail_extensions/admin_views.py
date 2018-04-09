import operator

from django.contrib.postgres.fields.jsonb import JSONField
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.db.models.expressions import RawSQL, OrderBy

from wagtail.contrib.modeladmin.views import IndexView

from .jsonfield_utils import jsonfield_path_split


class _SearchInJSONFieldsIndexViewMixin(IndexView):
    """
    Search inside `JSONField` paths in addition to standard Django model fields
    using JSON data paths defined in a `json_search_fields` attribute on
    Wagtail's `ModelAdmin`.

    For example, given 'data' is a `JSONField`:

        class MyIndexView(_SearchInJSONFieldsIndexViewMixin, IndexView):
            pass

        class MyAdmin(ModelAdmin):
            index_view_class = MyIndexView
            json_search_fields = (
                'data__title',
                'data__name__full',
            )
            search_fields = ('pk',)  # Must not be empty

    NOTE: You **must** have a non-empty `search_fields` definition in addition
    to `json_search_fields` for the search fields to be exposed properly in the
    admin, so set this to at least some minimal value.
    """

    def get_search_results(self, request, queryset, search_term):
        json_search_fields = getattr(
            self.model_admin, 'json_search_fields', [])
        if json_search_fields and not self.search_fields:
            # TODO Use a more appropriate exception subclass
            raise Exception(
                u"'search_fields' must be defined on admin %s before "
                u"'json_search_fields' will work properly. Define at least "
                u"`search_fields = ('pk',)` if no other fields are "
                u"appropriate for searching"
                % type(self.model_admin)
            )

        # Apply standard search as defined with `search_fields`
        search_qs, use_distinct = \
            super(_SearchInJSONFieldsIndexViewMixin, self).get_search_results(
                request, queryset, search_term)

        # Apply `JSONField` search as defined with `json_search_fields` by
        # reproducing key parts of `IndexView.get_search_results()` but without
        # the `use_distinct` checks which trigger `FieldDoesNotExist` errors
        # because Django does not (yet) support `distinct()` for `JSONField`s
        if search_term and json_search_fields:
            json_search_qs = queryset
            orm_lookups = ['%s__icontains' % str(search_field)
                           for search_field in json_search_fields]
            for bit in search_term.split():
                or_queries = [models.Q(**{orm_lookup: bit})
                              for orm_lookup in orm_lookups]
                json_search_qs = json_search_qs.filter(
                    reduce(operator.or_, or_queries))
            search_qs |= json_search_qs

        return search_qs, use_distinct


class _OrderByJSONFieldsIndexViewMixin(IndexView):
    """
    Permit ordering by `JSONField` paths in an admin listing view by basing
    your custom index view on this mixin, then define methods to display and
    order by nested paths.

    For example, given 'data' is a `JSONField`:

        class MyIndexView(_OrderByJSONFieldsIndexViewMixin, IndexView):
            pass

        class MyAdmin(ModelAdmin):
            index_view_class = MyIndexView
            list_display = ('name_full',)

            def name_full(self, obj):
                return obj.data.get('name', {}).get('full')
            name_full.admin_order_field = 'data__name__full'
    """

    def get_ordering(self, request, queryset):
        # Apply standard ordering, may return `JSFONField` paths that will blow
        # up unless amended below
        ordering = super(_OrderByJSONFieldsIndexViewMixin, self) \
            .get_ordering(request, queryset)

        # Apply adjustments for `JSONField` ordering by adjusting the SQL
        # fragments when necessary. This is required because Django does not
        # (yet) support ordering by `JSONField` paths in `order_by()`
        updated_ordering = []
        for order_path in ordering:
            field_name, json_path = jsonfield_path_split(order_path)
            descending = field_name[0] == '-'
            if descending:
                field_name = field_name[1:]
            try:
                model_field = self.model._meta.get_field(field_name)
            except FieldDoesNotExist:
                # Catch errors looking up field aliases like 'pk'
                model_field = None
            if isinstance(model_field, JSONField):
                # Replace standard Django field path string with custom SQL
                # TODO Support type coercion, e.g. '__int' suffix to cast value
                # in DB to integer before ordering, or '__lower' for lowercase
                # See https://stackoverflow.com/questions/36641759/django-1-9-jsonfield-order-by/44067258#44067258
                sql = RawSQL(
                    field_name + '#>>%s',
                    ("{%s}" % ','.join(json_path),)
                )
                updated_ordering.append(OrderBy(sql, descending=descending))
            else:
                # No change necessary
                updated_ordering.append(order_path)

        return updated_ordering
