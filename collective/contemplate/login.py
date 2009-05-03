from zope import component
from zope import event

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

    info = logged_in.principal.portal_types.getTypeInfo(
        logged_in.principal.portal_membership.memberarea_type)
    template = info.getTemplate(container)
    if template is None:
        return
    orig, source = template

    sm = SecurityManagement.getSecurityManager()
    SecurityManagement.newSecurityManager(
        None,
        logged_in.principal.portal_url.getPortalObject().getOwner())
    result, = container.manage_pasteObjects(
        source.manage_copyObjects([orig.getId()]))
    container.manage_renameObject(result['new_id'], safe_member_id)
    SecurityManagement.setSecurityManager(sm)

    added = container[safe_member_id]
    owner.changeOwnershipOf(added)
    event.notify(interfaces.TemplateCopiedEvent(added, orig))
