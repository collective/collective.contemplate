from Products.CMFCore.utils import getToolByName


def changeOwnershipOf(object, userid=None):
    membership = getToolByName(object, 'portal_membership')

    if userid is None:
        userid = membership.getAuthenticatedMember().getId()

    acl_users = getToolByName(object, 'acl_users')
    user = acl_users.getUserById(userid)
    if user is None:
        # The user could be in the top level acl_users folder in
        # the Zope root, in which case this should find him:
        user = membership.getMemberById(userid).getUser()
        if user is None:
            raise KeyError(
                'Only retrievable users in this site can be made '
                'owners.')

    object.changeOwnership(user, 1)
    fixOwnerRole(object, userid)

    _path = object.portal_url.getRelativeContentURL(object)
    for brain in object.portal_catalog.unrestrictedSearchResults(
        path={'query': _path, 'level': 1}):
        obj = brain.getObject()
        fixOwnerRole(obj, userid)
        obj.reindexObject(
            object._cmf_security_indexes + ('Creator',))


def fixOwnerRole(object, user_id):
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
