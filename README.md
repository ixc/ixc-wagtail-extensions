Extensions to help us build Wagtail sites
=========================================


Using JSONFields in Admin
-------------------------

### Pretty rendering of JSONField

Render JSON data from a `JSONField` model fields as a nice interactive widget
in the Wagtail admin using `wagtail_extensions.widgets.JSONFieldWidget`.
Without this, `JSONField` fields are displayed as ugly plain editable text.

For Wagtail pages, specify this widget directly in the panels definition:

    content_panels = Page.content_panels + [
        FieldPanel("json", widget=JSONFieldWidget)
    ]

For standard models:

* define a custom admin form class based on the admin helper class
  `wagtail_extensions.forms._PrettyJSONFieldForm`
* set your model's `base_form_class` attribute to point this form class.

The UI widget is from http://kevinmickey.github.io/django-prettyjson/

Original ticket: https://github.com/ixc/agsa/issues/187

### Filter by nested data

Make data fields nested in `JSONField`s available for filtering in the admin
by distinct values using the
`wagtail_extensions.admin.jsonfield_simplelistfilter_builder` function in
the admin's `list_filter` attribute:

    list_filter = (
        jsonfield_simplelistfilter_builder(
            'data__background__nationality',  # Path in 'data' JSONField
            'nationality',  # GET parameter name to use
            title='nationality'),  # Optional human-friendly title for filter
    )

### Search by nested data

Make data fields nested in `JSONField`s available for searching in the admin,
in addition to standard Django model fields, by setting a custom `IndexView`
class for your admin based on
`wagtail_extensions.admin_views._SearchInJSONFieldsIndexViewMixin` and
specifying search paths in a `json_search_fields` attribute on
Wagtail's `ModelAdmin`.

For example, given 'data' is a `JSONField`:

    class MyIndexView(_SearchInJSONFieldsIndexViewMixin, IndexView):

        json_search_fields = (
            'data__title',
            'data__name__full',
        )

        search_fields = ('pk',)  # Must not be empty

NOTE: You **must** have a non-empty `search_fields` definition in addition
to `json_search_fields` for the search fields to be exposed properly in the
admin, so set this to at least some minimal value.

Original ticket: https://github.com/ixc/agsa/issues/188




TODOs:

* Show nested data in listing columns
* Order by nested data
* Expose nested JSONField data on admin forms


Other Admin extensions
----------------------

### Multiple admin views of a single model

To avoid the very tight coupling we normally have in Wagtail & Django between
a model and its management in the admin, we have helper classes you can use
to provide multiple different admin views for a single model.

This is particularly helpful for document-centric models where we can store
multiple different document structures in the same model and need to expose
these differently in the admin, but it may be useful in other situations as
well.

The multiple admins work through custom URL helpers classes that you link
to the model admins.

To provide multiple admins:

* for each admin view you want, define a custom URL helper class based on
  `wagtail_extensions.admin_helpers.BasePageAdminURLHelper` for a Wagtail
  page, or `wagtail_extensions.admin_helpers.BaseAdminURLHelper` for a
  standard model
* optionally override the default URL-building attributes on your URL helper
  classes to customise the URL that will be provided in the admin, for example
  an admin view focussed on Artwork documents might have:
      url_prefix = 'artwork'
* define a separate Wagtail `ModelAdmin` class for each admin view you want.
  For each of these:
  * set `url_helper_class` to the corresponding URL helper class
  * set `menu_label` to identify the view, e.g. "Artwork documents"
  * configure the admin as appropriate for the view, e.g. with specific
    `list_display`, `list_filter`, `get_queryset(self, request)` and
    field methods.
* register the multiple admins with Wagtail as usual via
  `modeladmin_register`

Original ticket: https://github.com/ixc/agsa/issues/190



TODOs:

* Rationale
* Diagram
* Risks and drawbacks
* Example models
* Bulk import of data
* Validation with Cerberus
