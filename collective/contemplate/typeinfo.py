from zope import interface
from zope import component
from zope import event

import Globals
import Acquisition

from Products.CMFCore import TypesTool

from collective.contemplate import interfaces

class TemplateTypeInfo(object):
    interface.implements(interfaces.ITemplateTypeInfo)

    meta_type = 'TemplateTypeInfo'

    def constructInstance(self, container, id, *args, **kw):
        """Copy a template if available"""
        template = self.getTemplate(container)
        if template is None:
            return super(
                TemplateTypeInfo, self).constructInstance(
                container, id, *args, **kw)
        orig, source = template
        result, = container.manage_pasteObjects(
            source.manage_copyObjects([orig.getId()]))
        # Acquisition workaround
        added = container[result['new_id']]
        self.changeOwnership(added)
        event.notify(
            interfaces.TemplateCopiedEvent(added, orig))
        return added
    
    def getTemplate(self, container):
        site = container.portal_url.getPortalObject()
        parent = container
        while parent is not None:
            template = component.queryMultiAdapter(
                (parent, self), interfaces.ITemplate)
            if template is not None:
                return template, parent
            if Acquisition.aq_base(parent) is site:
                return
            parent = Acquisition.aq_parent(parent)

class TemplateTypeInformation(TemplateTypeInfo,
                              TypesTool.TypeInformation):

    meta_type = 'TemplateTypeInformation'

Globals.InitializeClass(TemplateTypeInformation)

class TemplateFactoryTypeInfo(TemplateTypeInfo,
                              TypesTool.FactoryTypeInformation):

    meta_type = 'TemplateFactoryTypeInfo'

Globals.InitializeClass(TemplateFactoryTypeInfo)

class TemplateScriptableTypeInfo(TemplateTypeInfo,
                                 TypesTool.ScriptableTypeInformation):

    meta_type = 'TemplateScriptableTypeInfo'

Globals.InitializeClass(TemplateScriptableTypeInfo)
