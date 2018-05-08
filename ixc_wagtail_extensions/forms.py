from django.contrib.postgres.forms.jsonb import JSONField

from wagtail.wagtailadmin.forms import WagtailAdminModelForm

from .widgets import JSONFieldWidget
from .jsonfield_utils import jsonfield_path_split


class _PrettyJSONFieldForm(WagtailAdminModelForm):
    """
    Render form fields backed by a `JSONField` with a pretty interactive
    widget.
    """

    def __init__(self, *args, **kwargs):
        super(_PrettyJSONFieldForm, self).__init__(*args, **kwargs)
        self.prettify_jsonfields()

    def prettify_jsonfields(self):
        for field_name, field in self.fields.items():
            if isinstance(field, JSONField):
                self.fields[field_name].widget = JSONFieldWidget()


class _ExposeJSONFieldDataAdminModelFormMixin(WagtailAdminModelForm):
    """
    Expose arbitrarily nested `JSONField` data as top-level form fields that
    are extra to the standard model fields included in the model form.

    To use this, subclass this class then add the form fields as usual along
    with corresponding entries in a `formfield_to_jsonfield_path` attribute,
    like so:

        class MyForm(_ExposeJSONFieldDataAdminModelFormMixin):
            slug = forms.CharField()
            name_full = forms.CharField()

            formfield_to_jsonfield_path = {
                'slug': 'data__slug',
                'name_full': 'data__name__full',
            }

    You then make the extra form fields available in the Wagtail admin by
    setting `base_form_class = MyForm` on your model and include the extra form
    names in standard `panels` or similar definitions.

    See http://docs.wagtail.io/en/v1.13.1/advanced_topics/customisation/page_editing_interface.html#customising-generated-forms
    """
    formfield_to_jsonfield_path = {}

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        initial = kwargs.get('initial', {})
        # Populate extra form fields with values from `JSONField`s in instance
        if instance:
            for formfield, json_path in \
                    self.formfield_to_jsonfield_path.items():
                field_name, json_path = jsonfield_path_split(json_path)
                d = getattr(instance, field_name)
                for path in json_path[:-1]:
                    d = d.get(path, {})
                initial[formfield] = d.get(json_path[-1])
            kwargs['initial'] = initial
        super(_ExposeJSONFieldDataAdminModelFormMixin, self) \
            .__init__(*args, **kwargs)

    def save(self, **kwargs):
        # Apply extra form field values back to `JSONField` paths in instance
        for formfield, json_path in \
                self.formfield_to_jsonfield_path.items():
            field_name, json_path = jsonfield_path_split(json_path)
            d = getattr(self.instance, field_name)
            for path in json_path[:-1]:
                if path not in d:
                    d[path] = {}
                d = d.get(path)
            d[json_path[-1]] = self.cleaned_data.pop(formfield)
        return super(_ExposeJSONFieldDataAdminModelFormMixin, self) \
            .save(**kwargs)
