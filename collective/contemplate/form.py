from zope import interface
from zope import component
from zope import event
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

    def createAndAdd(self, *args, **kw):
        if self.template is None:
            return super(
                TemplateAddForm, self).createAndAdd(*args, **kw)
        destination = Acquisition.aq_inner(self.adding.context)
        source = Acquisition.aq_inner(self.container)
        result, = destination.manage_pasteObjects(
            source.manage_copyObjects([self.context.getId()]))
        # Acquisition workaround
        self.__dict__['context'] = added = destination[
            result['new_id']]
        self.changeOwnership(added)
        event.notify(
            interfaces.TemplateCopiedEvent(added, self.context))
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
        object.plone_utils.changeOwnershipOf(
            object, user_id, recursive=1)
        object.setCreators((user_id,))
