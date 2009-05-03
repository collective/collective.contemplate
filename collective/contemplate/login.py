from zope import component

from Products.PluggableAuthService.interfaces import events
from Products.PlonePAS import utils 

@component.adapter(events.IUserLoggedInEvent)
def createMemberArea(event):
    """Use invokeFactory so that the template will be used"""
    if not hasattr(event.principal, 'Members'):
        return
    safe_member_id = utils.cleanId(event.principal.getId())
    if event.principal.Members.hasObject(safe_member_id):
        return
    event.principal.Members.invokeFactory(
        type_name=event.principal.portal_membership.memberarea_type,
        id=safe_member_id)
