import sys
import warnings
from cgi import escape

from zope.event import notify
from zope.lifecycleevent import ObjectMovedEvent
from zope.lifecycleevent import ObjectCopiedEvent
from zope.container.contained import notifyContainerModified

from ZODB.POSException import ConflictError
from Acquisition import aq_base
from Acquisition import aq_parent
from App.Dialogs import MessageDialog
from webdav.Lockable import ResourceLockedError
from OFS.event import ObjectWillBeMovedEvent
from OFS.event import ObjectClonedEvent
from OFS.subscribers import compatibilityCall
from OFS.CopySupport import CopyError
from OFS.CopySupport import eNotSupported


def moveObject(ob, newParent, newName=None):
    """Move an object to a new container.
    """
    oldParent = aq_parent(ob)
    oldName = ob.getId()

    try:
        newParent._checkId(newName)
    except:
        raise CopyError(MessageDialog(
            title='Invalid Id',
            message=sys.exc_info()[1],
            action='manage_main'))

    ob = oldParent._getOb(oldName)

    if ob.wl_isLocked():
        raise ResourceLockedError('Object "%s" is locked via WebDAV'
                                    % ob.getId())
    if not ob.cb_isMoveable():
        raise CopyError(eNotSupported % escape(oldName))
    newParent._verifyObjectPaste(ob)

    try:
        ob._notifyOfCopyTo(newParent, op=1)
    except ConflictError:
        raise
    except:
        raise CopyError(MessageDialog(
            title="Rename Error",
            message=sys.exc_info()[1],
            action='manage_main'))

    notify(ObjectWillBeMovedEvent(ob, oldParent, oldName, newParent, newName))

    # try to make ownership explicit so that it gets carried
    # along to the new location if needed.
    ob.manage_changeOwnershipType(explicit=1)

    try:
        oldParent._delObject(oldName, suppress_events=True)
    except TypeError:
        oldParent._delObject(oldName)
        warnings.warn(
            "%s._delObject without suppress_events is discouraged." %
            oldParent.__class__.__name__, DeprecationWarning)
    ob = aq_base(ob)
    ob._setId(newName)

    # Note - because a rename always keeps the same context, we
    # can just leave the ownership info unchanged.
    try:
        newParent._setObject(newName, ob, set_owner=0, suppress_events=True)
    except TypeError:
        newParent._setObject(newName, ob, set_owner=0)
        warnings.warn(
            "%s._setObject without suppress_events is discouraged." %
            newParent.__class__.__name__, DeprecationWarning)
    ob = newParent._getOb(newName)

    notify(ObjectMovedEvent(ob, oldParent, oldName, newParent, newName))
    notifyContainerModified(oldParent)
    if aq_base(oldParent) is not aq_base(newParent):
        notifyContainerModified(newParent)

    ob._postCopy(newParent, op=1)
    # try to make ownership implicit if possible
    ob.manage_changeOwnershipType(explicit=0)

    return None


def copyObject(ob, newParent, newName=None):
    """Move an object to a new container.
    """
    oldParent = aq_parent(ob)
    orig_id = ob.getId()
    if not ob.cb_isCopyable():
        raise CopyError(eNotSupported % escape(orig_id))

    try:
        ob._notifyOfCopyTo(newParent, op=0)
    except ConflictError:
        raise
    except:
        raise CopyError(MessageDialog(
            title="Copy Error",
            message=sys.exc_info()[1],
            action='manage_main'))

    if newName is None:
        id = newParent._get_id(orig_id)
    else:
        id = newName

    orig_ob = ob
    ob = ob._getCopy(oldParent)
    ob._setId(id)
    notify(ObjectCopiedEvent(ob, orig_ob))

    newParent._setObject(id, ob)
    ob = newParent._getOb(id)
    ob.wl_clearLocks()

    ob._postCopy(newParent, op=0)

    compatibilityCall('manage_afterClone', ob, ob)

    notify(ObjectClonedEvent(ob))

    return ob
