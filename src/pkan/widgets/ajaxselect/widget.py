# -*- coding: utf-8 -*-
"""An advanced AJAX select widget for Plone."""
from Acquisition import aq_inner
from pkan.dcatapde import _
from pkan.dcatapde.api.functions import restore_user
from pkan.dcatapde.api.functions import work_as_admin
from pkan.dcatapde.constants import DEACTIVE_STATE
from pkan.widgets.base import AddItemMixin
from plone import api
from plone.app.z3cform.interfaces import IAjaxSelectWidget
from plone.app.z3cform.widget import AjaxSelectWidget
from Products.CMFCore.utils import getToolByName
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implementer_only
from zope.schema.interfaces import IField
from zope.security import checkPermission


class IAjaxSelectAddWidget(IAjaxSelectWidget):
    """Marker interface for the advanced AjaxSelectWidget."""


@implementer_only(IAjaxSelectAddWidget)
class AjaxSelectAddWidget(AjaxSelectWidget, AddItemMixin):
    """An advanced related items widget for Plone."""

    def render(self):
        widget = super(AjaxSelectAddWidget, self).render()

        if self.mode != 'input':
            return widget

        if self.content_type is None:
            return widget

        return self.render_widget(widget)

    def related_items(self):
        related = self.value
        if not related:
            return ()
        related = related.split(self.separator)
        brains = self.related2brains(related)
        return self.collect_data(brains)

    def related2brains(self, related):
        """Return a list of brains based on a list of UIDs.

        Will filter relations if the user has no permission to access
        the content.
        :param related: related items
        :type related: list of UIDs
        :return: list of catalog brains
        """
        catalog = api.portal.get_tool(name='portal_catalog')
        user = work_as_admin()
        brains = catalog(UID=related)
        restore_user(user)
        if brains:
            # build a position dict by iterating over the items once
            positions = dict([(v, i) for (i, v) in enumerate(related)])
            # We need to keep the ordering intact
            res = list(brains)

            def _key(brain):
                return positions.get(brain.UID, -1)
            res.sort(key=_key)
        return brains

    def collect_data(self, brains):
        data = []
        wf_tool = getToolByName(self.context, 'portal_workflow')
        for brain in brains:
            user = work_as_admin()
            obj = brain.getObject()
            restore_user(user)
            state = wf_tool.getInfoFor(aq_inner(obj), 'pkan_state', None)
            permission = checkPermission('zope2.View', obj)
            if permission:
                title = obj.Title()
                if state == DEACTIVE_STATE:
                    title += _(u':Deprecated')
            else:
                title = _(u'Permission Denied')
            data.append({
                'item': brain,
                'title': title,
                'permission': permission,
            })
        return data


@adapter(IField, IFormLayer)
@implementer(IFieldWidget)
def AjaxSelectAddFieldWidget(field, request, extra=None):
    """An advanced ajax select widget for Plone."""
    if extra is not None:
        request = extra
    return FieldWidget(field, AjaxSelectAddWidget(request))
