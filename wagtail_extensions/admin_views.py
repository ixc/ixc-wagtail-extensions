import operator

from django.db import models

from wagtail.contrib.modeladmin.views import IndexView


class _SearchInJSONFieldsIndexViewMixin(IndexView):
    """
    Search inside `JSONField` paths in addition to standard Django model fields
    using JSON data paths defined in a `json_search_fields` attribute on
    Wagtail's `ModelAdmin`.

    For example, given 'data' is a `JSONField`:

        class MyIndexView(_SearchInJSONFieldsIndexViewMixin, IndexView):

            json_search_fields = (
                'data__title',
                'data__name__full',
            )

    NOTE: You **must** have a non-empty `search_fields` definition in addition
    to `json_search_fields` for the search fields to be exposed properly in the
    admin, so set this to at least some minimal value like

            `search_fields = ('pk',)`
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
