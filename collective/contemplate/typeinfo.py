from zope import interface
from zope import component
from zope import event

import Globals
import Acquisition

from Products.CMFCore import TypesTool

from collective.contemplate import interfaces
from collective.contemplate import owner

class TemplateTypeInfo(object):
    """Template Type Information"""
    interface.implements(interfaces.ITemplateTypeInfo)

    meta_type = 'TemplateTypeInfo'

    _properties = (
        {'id':'reserved_id', 'type': 'string', 'mode':'w',
         'label':'Reserved ID'},)

    reserved_id = None

    def constructInstance(self, container, id=None, *args, **kw):
        """Copy a template if available"""
        template = self.getTemplate(container)
        if template is None:
            return super(
                TemplateTypeInfo, self).constructInstance(
                container, id, *args, **kw)
        orig, source = template
        result, = container.manage_pasteObjects(
            source.manage_copyObjects([orig.getId()]))
        if id:
            container.manage_renameObject(result['new_id'], id)
            added = container[id]
        else:
            added = container[result['new_id']]
            
        owner.changeOwnershipOf(added)
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

    def isConstructionAllowed(self, container):
        """Not allowed if reserved id is already occupied"""
        if self.reserved_id and container.hasObject(self.reserved_id):
            return False
        return super(
            TemplateTypeInfo, self).isConstructionAllowed(container)

class TemplateTypeInformation(TemplateTypeInfo,
                              TypesTool.TypeInformation):
    """Template Type Information"""

    meta_type = 'TemplateTypeInformation'
    _properties = (TypesTool.TypeInformation._properties +
                   TemplateTypeInfo._properties)

Globals.InitializeClass(TemplateTypeInformation)

class TemplateFactoryTypeInfo(TemplateTypeInfo,
                              TypesTool.FactoryTypeInformation):
    """Template Factory Type Information"""

    meta_type = 'TemplateFactoryTypeInfo'
    _properties = (TypesTool.FactoryTypeInformation._properties +
                   TemplateTypeInfo._properties)

Globals.InitializeClass(TemplateFactoryTypeInfo)

class TemplateScriptableTypeInfo(TemplateTypeInfo,
                                 TypesTool.ScriptableTypeInformation):
    """Template Scriptable Type Information"""

    meta_type = 'TemplateScriptableTypeInfo'
    _properties = (TypesTool.ScriptableTypeInformation._properties +
                   TemplateTypeInfo._properties)

Globals.InitializeClass(TemplateScriptableTypeInfo)
