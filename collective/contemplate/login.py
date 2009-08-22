from zope import component
from zope import event

import Acquisition
from AccessControl import SecurityManagement

from Products.PluggableAuthService.interfaces import events
from Products.PlonePAS import utils 

from collective.contemplate import interfaces
from collective.contemplate import owner

@component.adapter(events.IUserLoggedInEvent)
def createMemberArea(logged_in):
    """Use the template if available"""
    if not hasattr(logged_in.principal, 'Members'):
        return
    safe_member_id = utils.cleanId(logged_in.principal.getId())
    container = logged_in.principal.Members
    if container.hasObject(safe_member_id):
        return
    createObjectAsPortalOwner(
        container, 
        type_name=container.portal_membership.memberarea_type,
        id_=safe_member_id)

def createObjectAsPortalOwner(container, type_name, id_):
    """Create an object as the portal owner"""
    info = interfaces.ITemplateTypeInfo(
        container.portal_types.getTypeInfo(type_name), None)
    if info is None:
        return
    template = info.getTemplate(container)
    if template is None:
        return
    source = Acquisition.aq_parent(Acquisition.aq_inner(template))
        
    sm = SecurityManagement.getSecurityManager()
    SecurityManagement.newSecurityManager(
        None,
        container.portal_url.getPortalObject().getOwner())
    result, = container.manage_pasteObjects(
        source.manage_copyObjects([template.getId()]))
    container.manage_renameObject(result['new_id'], id_)
    SecurityManagement.setSecurityManager(sm)

    added = container[id_]
    owner.changeOwnershipOf(added)
    event.notify(interfaces.TemplateCopiedEvent(added, template))

    return added
