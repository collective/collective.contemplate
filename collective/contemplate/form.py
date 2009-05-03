from zope import component

import Acquisition

class TemplateAddForm(object):

    def __init__(self, *args, **kw):
        super(TemplateAddForm, self).__init__(*args, **kw)
        self.adding = self.context
        self.template = self.adding.context.portal_types.getTypeInfo(
            self.type_name).getTemplate(
            Acquisition.aq_inner(self.adding.context))
        if self.template is not None:
            self.context, self.container = self.template

    def createAndAdd(self, data):
        """Delegate to the type info"""
        destination = Acquisition.aq_inner(self.adding.context)
        new_id = destination.invokeFactory(
            type_name=self.type_name, **data)
        return destination[new_id]
        
    def nextURL(self):
        return str(component.getMultiAdapter(
            (self.added, self.request), name=u"absolute_url"))

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

    def changeOwnership(self, object):
        membership = object.portal_membership
        acl_users = self.context.acl_users
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

        _path = self.context.portal_url.getRelativeContentURL(object)
        for brain in self.context.portal_catalog(
            path={'query':_path,'level':1}):
            obj = brain.getObject()
            self.fixOwnerRole(obj, userid)
            obj.reindexObject(
                self.context._cmf_security_indexes+('Creator',))
