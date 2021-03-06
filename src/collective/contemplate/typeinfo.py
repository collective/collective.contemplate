from zope import interface
from zope import component
from zope import event

import Globals
import Acquisition

from Products.CMFCore.utils import getToolByName
from Products.CMFCore import TypesTool

from collective.contemplate import interfaces
from collective.contemplate import owner
from collective.contemplate import ofs


class TemplateTypeInfo(object):
    """Template Type Information"""
    interface.implements(interfaces.ITemplateTypeInfo)

    meta_type = 'TemplateTypeInfo'

    _properties = (
        {'id': 'reserved_id', 'type': 'string', 'mode': 'w',
         'label': 'Reserved ID'},
        {'id': 'global_uid', 'type': 'string', 'mode': 'w',
         'label': 'Global Template UID'},)

    reserved_id = None

    def _constructInstance(self, container, id=None, *args, **kw):
        """Copy a template if available"""
        template = Acquisition.aq_inner(self.getTemplate(container))
        if template is None:
            return super(
                TemplateTypeInfo, self)._constructInstance(
                container, id, *args, **kw)
        added = ofs.copyObject(template, container, newName=id)

        # Clear the copy flag or the reference catalogs might not be
        # updated on reindexObject()
        if hasattr(added, '_v_is_cp'):
            del added._v_is_cp

        owner.changeOwnershipOf(added)
        if args or kw:
            added.edit(*args, **kw)
        event.notify(
            interfaces.TemplateCopiedEvent(added, template))
        return added

    def getTemplate(self, container):
        site = getToolByName(container, 'portal_url').getPortalObject()
        parent = container
        container_base = Acquisition.aq_base(container)
        while parent is not None:
            template = component.queryMultiAdapter(
                (parent, self), interfaces.ITemplate)
            parent_base = Acquisition.aq_base(parent)
            if template is not None and (
                parent_base is container_base or not
                interfaces.IContainerOnlyTemplate.providedBy(template)
                ):
                return template
            if Acquisition.aq_base(parent) is site:
                return
            parent = Acquisition.aq_parent(parent)
        return interfaces.ITemplate(self, None)

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
