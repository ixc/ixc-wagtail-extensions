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
