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

Original ticket: https://github.com/ixc/agsa/issues/188

### Display and order by nested data

Django does not (yet) support using paths to data nested in `JSONField`s for
display in admin listing columns, or for ordering, but you can display this
data indirectly using methods on Wagtail's `ModelAdmin` as in standard Django.

For example, given 'data' is a `JSONField` with 'name' > 'full' content:

    class MyAdmin(ModelAdmin):
        list_display = ('name_full',)

        def name_full(self, obj):
            return obj.data.get('name', {}).get('full')

In Wagtail you can also enable these methods for ordering by setting the
`admin_order_field` on the attribute to a field path. Paths to nested data are
not supported by the normal paths, but you can add this support by setting a
custom `IndexView` class for your admin based on
`wagtail_extensions.admin_views._OrderByJSONFieldsIndexViewMixin`.

Here is an extensions of the example above to permit ordering by nested fields.
Note the custom index view class, and setting an attribute on the admin method
to add ordering:

    class MyIndexView(_OrderByJSONFieldsIndexViewMixin, IndexView):
        pass

    class MyAdmin(ModelAdmin):
        index_view_class = MyIndexView
        list_display = ('name_full',)

        def name_full(self, obj):
            return obj.data.get('name', {}).get('full')
        name_full.admin_order_field = 'data__name__full'

NOTE: There is not yet support for coercing `JSONField` content to different
data types to give the expected ordering, so results will currently be entirely
up to the DB's chosen ordering approach.

### Expose nested JSONField data in Admin create/edit form

To make it easier to update or override data nested within `JSONField` fields
on a model, you can expose arbitrarily nested data as top-level form fields
in the admin by creating a custom form based on
`wagtail_extensions.forms._ExposeJSONFieldDataAdminModelFormMixin` with extra
form fields and an attribute `formfield_to_jsonfield_path` to map the relevant
paths within the `JSONField`.

For example, given 'data' is a `JSONField` from which you want to expose the
*slug* and *name > full* nested data:

    class MyForm(_ExposeJSONFieldDataAdminModelFormMixin):
        # Extra form fields added to model fields
        slug = forms.CharField()
        name_full = forms.CharField()

        # Mapping from form field name to path in JSONField
        formfield_to_jsonfield_path = {
            'slug': 'data__slug',
            'name_full': 'data__name__full',
        }


    class MyModel(models.Model):
        # Usual model definitions here...

        # Custom model admin form to expose nested `JSONField` data
        base_form_class = MyForm

        panels = [
            # Exposed `JSONField` data as made available by
            # `_ExposeJSONFieldDataAdminModelFormMixin`
            FieldPanel('slug'),
            FieldPanel('name_full'),

            # Continued... rest of standard model fields go here
        ]

Note: Because custom Admin forms are defined directly on the Model class in
Wagtail -- absurd as that is -- it is not currently possible to expose
different fields if you have multiple different admin views on the same model.
This is a general problem for panels/fields defined on models.


Other Admin extensions
----------------------

### Show consistent title in menu and top of index listing

To show the title set in Wagtail's optional `ModelAdmin.menu_label` as the
title of admin listing views instead of the default verbose model name, so the
admin has consistent titles in the menu and atop the listing page, set a custom
`IndexView` class for your admin based on
`wagtail_extensions.admin_views._ConsistentTitlesIndexViewMixin`:

    class MyIndexView(_ConsistentTitlesIndexViewMixin, IndexView):
        pass

    class MyAdmin(ModelAdmin):
        index_view_class = MyIndexView
        menu_label = 'Title to be made consistent'

This customisation will mainly be useful if you have multiple admin views of
a single model, but might be nice to have in other places where we want
consistent naming through the admin UI.

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
