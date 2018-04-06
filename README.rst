=========================================
Extensions to help us build Wagtail sites
=========================================


Using JSONFields
================

Pretty rendering of JSONField
-----------------------------

Render JSON data from a ``JSONField`` model fields as a nice interactive widget
in the Wagtail admin using ``wagtail_extensions.widgets.JSONFieldWidget``.
Without this, ``JSONField`` fields are displayed as ugly plain editable text.

For Wagtail pages, specify this widget directly in the panels definition::

    content_panels = Page.content_panels + [
        FieldPanel("json", widget=JSONFieldWidget)
    ]

For standard models:

* define a custom admin form class based on the admin helper class
  ``wagtail_extensions.forms._PrettyJSONFieldForm``
* set your model's ``base_form_class`` attribute to point this form class.

The UI widget is from http://kevinmickey.github.io/django-prettyjson/

Original ticket: https://github.com/ixc/agsa/issues/187



Admin index listing
-------------------

* Show nested data in listing columns
* Order by nested data
* Search by nested data
* Filter by nested data


Document-centric models for externally synced data
==================================================

* Rationale
* Diagram
* Risks and drawbacks
* Example models
* Multiple admin views of a single model
* Expose nested JSONField data on admin forms
* Bulk import of data
* Validation with Cerberus
