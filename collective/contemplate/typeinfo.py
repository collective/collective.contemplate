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

    _properties = (
        {'id':'reserved_id', 'type': 'string', 'mode':'w',
         'label':'Reserved ID'},)

    reserved_id = None

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
        self.changeOwnershipOf(added)
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

    def changeOwnershipOf(self, object):
        membership = object.portal_membership
        acl_users = object.acl_users
        userid = membership.getAuthenticatedMember().getId()
        user = acl_users.getUserById(userid)
        if user is None:
            # The user could be in the top level acl_users folder in
            # the Zope root, in which case this should find him:
            user = membership.getMemberById(userid)
            if user is None:
                raise KeyError(
                    'Only retrievable users in this site can be made '
                    'owners.')

        object.changeOwnership(user, 1)
        self.fixOwnerRole(object, userid)

        _path = object.portal_url.getRelativeContentURL(object)
        for brain in object.portal_catalog(
            path={'query':_path,'level':1}):
            obj = brain.getObject()
            self.fixOwnerRole(obj, userid)
            obj.reindexObject(
                object._cmf_security_indexes+('Creator',))

    def fixOwnerRole(self, object, user_id):
        # Get rid of all other owners
        owners = object.users_with_local_role('Owner')
        for o in owners:
            roles = list(object.get_local_roles_for_userid(o))
            roles.remove('Owner')
            if roles:
                object.manage_setLocalRoles(o, roles)
            else:
                object.manage_delLocalRoles([o])
        # Fix for 1750
        roles = list(object.get_local_roles_for_userid(user_id))
        roles.append('Owner')
        object.manage_setLocalRoles(user_id, roles)
        object.setCreators((user_id,))

    def isConstructionAllowed(self, container):
        """Not allowed if reserved id is already occupied"""
        if self.reserved_id and container.hasObject(self.reserved_id):
            return False
        return super(
            TemplateTypeInfo, self).isConstructionAllowed(container)

class TemplateTypeInformation(TemplateTypeInfo,
                              TypesTool.TypeInformation):

    meta_type = 'TemplateTypeInformation'
    _properties = (TypesTool.TypeInformation._properties +
                   TemplateTypeInfo._properties)

Globals.InitializeClass(TemplateTypeInformation)

class TemplateFactoryTypeInfo(TemplateTypeInfo,
                              TypesTool.FactoryTypeInformation):

    meta_type = 'TemplateFactoryTypeInfo'
    _properties = (TypesTool.FactoryTypeInformation._properties +
                   TemplateTypeInfo._properties)

Globals.InitializeClass(TemplateFactoryTypeInfo)

class TemplateScriptableTypeInfo(TemplateTypeInfo,
                                 TypesTool.ScriptableTypeInformation):

    meta_type = 'TemplateScriptableTypeInfo'
    _properties = (TypesTool.ScriptableTypeInformation._properties +
                   TemplateTypeInfo._properties)

Globals.InitializeClass(TemplateScriptableTypeInfo)
