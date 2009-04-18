from zope import interface
from zope import component
from zope.app.component import hooks

import Acquisition

from collective.contemplate import interfaces

class TemplateAddForm(object):
    interface.implements(interfaces.ITemplateForm)

    def __init__(self, *args, **kw):
        super(TemplateAddForm, self).__init__(*args, **kw)
        self.adding = self.context
        self.template = self.getTemplate()
        if self.template is not None:
            self.context, self.container = self.template

    def create(self, *args, **kw):
        if self.template is None:
            return super(TemplateAddForm, self).create(*args, **kw)
        result, = self.adding.context.manage_pasteObjects(
            self.container.manage_copyObjects(
                [self.context.getId()]))
        self.__dict__['context'] = added = self.adding.context[
            result['new_id']]
        self.changeOwnership(added)
        return added

    def nextURL(self):
        return str(component.getMultiAdapter(
            (self.added, self.request), name=u"absolute_url"))
    
    def getTemplate(self):
        site = Acquisition.aq_base(hooks.getSite())
        container = Acquisition.aq_inner(self.context.context)
        while container is not None:
            template = component.queryMultiAdapter(
                (container, self), interfaces.ITemplate)
            if template is not None:
                return template, container
            if Acquisition.aq_base(container) is site:
                return
            container = Acquisition.aq_parent(container)

    def changeOwnership(self, object):
        membership = object.portal_membership
        user_id = membership.getAuthenticatedMember().getId()
        object.plone_utils.changeOwnershipOf(object, user_id)
        object.setCreators((user_id,))
