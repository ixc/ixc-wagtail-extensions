from django.urls import reverse
from django.utils.http import urlquote

from wagtail.contrib.modeladmin.helpers import AdminURLHelper


class BaseAdminURLHelper(AdminURLHelper):
    """
    Base class for all AdminURLHelper classes that will be
    used for a simple django models (not Pages).
    Inherit all admin url helper classes from this class.
    """
    url_prefix = 'custom'
    url_suffix = None
    separator_sign = '-'
    model_name_part = None

    def __init__(self, *args, **kwargs):
        super(BaseAdminURLHelper, self).__init__(*args, **kwargs)
        self.model_name_part = self.separator_sign.join(
            i for i in [self.url_prefix, self.opts.model_name, self.url_suffix]
            if i)

    def _get_action_url_pattern(self, action):
        if action == 'index':
            return r'^%s/%s/$' % (self.opts.app_label, self.model_name_part)
        return r'^%s/%s/%s/$' % (self.opts.app_label, self.model_name_part,
                                 action)

    def _get_object_specific_action_url_pattern(self, action):
        return r'^%s/%s/%s/(?P<instance_pk>[-\w]+)/$' % (
            self.opts.app_label, self.model_name_part, action)

    def get_action_url_name(self, action):
        return '%s_%s_modeladmin_%s' % (
            self.opts.app_label, self.model_name_part, action)

    @property
    def index_url(self):
        return self.get_action_url('index')

    @property
    def create_url(self):
        return self.get_action_url('create')


class BasePageAdminURLHelper(BaseAdminURLHelper):
    """
    Base class for all BaseAdminURLHelper classes that will be
    used for a wagtail Pages (not django models).
    Inherit all admin url helper classes from this class.
    """

    def get_action_url(self, action, *args, **kwargs):
        if action in ('add', 'edit', 'delete', 'unpublish', 'copy'):
            url_name = 'wagtailadmin_pages:%s' % action
            target_url = reverse(url_name, args=args, kwargs=kwargs)

            return '%s?next=%s' % (target_url, urlquote(self.index_url))

        return super(BasePageAdminURLHelper, self).get_action_url(
            action, *args, **kwargs)
