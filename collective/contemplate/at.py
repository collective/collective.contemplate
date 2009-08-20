from urlparse import urlsplit

import transaction
from zope import interface
from zope import component

import Acquisition
from ZPublisher import Publish
from ZPublisher import mapply
from Products.Five.browser import pagetemplatefile

from Products.Archetypes import interfaces as at_ifaces

from collective.contemplate import interfaces
from collective.contemplate import form
from collective.contemplate import owner

@interface.implementer(interfaces.ITemplate)
@component.adapter(
    at_ifaces.IReferenceable, interfaces.ITemplateTypeInfo)
def getTemplateFromContainer(container, type_info):
    refs = [ref for ref in container.getRefs(
        relationship='contemplate.%s' % type_info.getId())
            if ref is not None]
    if len(refs) == 0:
        return
    assert len(refs) == 1, (
        'More than one template found for %s: %r' % (
            type_info.getId(), refs))
    return refs[0]

@interface.implementer(interfaces.ITemplate)
@component.adapter(interfaces.ITemplateTypeInfo)
def getTemplateFromTypeInfo(type_info):
    uid = type_info.getProperty('global_uid')
    if uid:
        return type_info.reference_catalog.lookupObject(uid)

class FormControllerTemplateAddForm(form.TemplateAddForm):

    index = pagetemplatefile.ZopeTwoPageTemplateFile('at.pt')

    def __call__(self):
        if self.template is None:
            # Fallback to the normal createObject script
            return mapply.mapply(
                Acquisition.aq_inner(
                    self.context.context).restrictedTraverse(
                    'createObject'),
                self.request.args, dict(type_name=self.type_name),
                Publish.call_object, 1, Publish.missing_name,
                Publish.dont_publish_class, self.request, bind=1)

        savepoint = transaction.savepoint(True)
        try:
            context = Acquisition.aq_inner(self.context)
            # Temporarily Make the current user the owner
            owner.changeOwnershipOf(context)
            # Lookup the form controller object at the template's edit
            # action and use it to process the form
            edit_action = self.getEdit(context)
            edit = context.restrictedTraverse(edit_action)
            controller = context.portal_form_controller
            controller_state = controller.getState(edit, is_validator=0)
            if 'form.submitted' in self.request:
                # Run the form controller validation
                controller_state = edit.getButton(
                    controller_state, self.request)
                validators = edit.getValidators(
                    controller_state, self.request).getValidators()
                controller_state = controller.validate(
                    controller_state, self.request, validators)
                if controller_state.getErrors():
                    # If there are errors then render this version of
                    # the form
                    return self.index(state=controller_state)
            else:
                # Form has not been submitted yet so simply render
                # this version of the form
                return self.index(state=controller_state)
        finally:
            # Undo the temporary change of ownership
            savepoint.rollback()

        # The form has been successully submitted, copy the template
        # and pass processing off to the real edit action
        added = self.createAndAdd(data=dict())
        controller_state.setContext(added)
        return added.restrictedTraverse(edit_action)()

    def createAndAdd(self, data):
        """Rename the object if the id widget is not visible to avoid
        'copy_of' ids"""
        added = super(FormControllerTemplateAddForm,
                      self).createAndAdd(data)
        if 'title' in self.request:
            added.setTitle(self.request['title'])
            added._renameAfterCreation()
            widget = added.getField('id').widget
            member = added.portal_membership.getAuthenticatedMember()
            member_visible_ids = member.getProperty(
                'visible_ids',
                added.portal_memberdata.getProperty('visible_ids'))
            widget_visible_ids = getattr(
                widget, 'ignore_visible_ids', None)
            if not (widget_visible_ids or member_visible_ids):
                self.request.form.pop('id', None)
        return added
        
    def getEdit(self, context):
        # From Products.CMFFormController.Actions.TraverseToAction
        action = 'edit'
        action_url = None
        haveAction = False

        actions_tool = context.portal_actions
        fti = context.getTypeInfo()

        try:
            # Test to see if the action is defined in the FTI as an
            # object or folder action
            action_ob = fti.getActionObject('object/'+action)
            if action_ob is None:
                action_ob = fti.getActionObject('folder/'+action)
            # Use portal actions here so we have a full expression
            # context
            ec = actions_tool._getExprContext(context)
            actiondict = action_ob.getAction(ec)
            haveAction = True
        except (ValueError, AttributeError):
            actions = actions_tool.listFilteredActionsFor(context)
            # flatten the actions as we don't care where they are
            actions = reduce(lambda x,y,a=actions:  x+a[y],
                             actions.keys(), [])
            for actiondict in actions:
                if actiondict['id'] == action:
                    haveAction = True
                    break
        # For traversal, our 'url' must be a traversable path
        if haveAction:
            action_url = actiondict['url'].strip()
            url_parts = urlsplit(action_url)
            # Check to see if we have a protocol, if so convert to a
            # path, otherwise make the assumption that we are dealing
            # with a physical path
            if url_parts[0] and self.request is not None:
                action_url = '/'.join(self.request.physicalPathFromURL(
                    action_url))
            else:
                action_url = url_parts[2]
        else:
            raise ValueError, 'No %s action found for %s' % (
                action, context.getId())

        # If we have CMF 1.5, the actual action_url may be hidden
        # behind a method alias. Attempt to resolve this
        try:
            if action_url:
                # If our url is a path, then we need to see if it
                # contains the path to the current object, if so we
                # need to check if the remaining path element is a
                # method alias
                possible_alias = action_url
                current_path = '/'.join(context.getPhysicalPath())
                if possible_alias.startswith(current_path):
                    possible_alias = possible_alias[
                        len(current_path)+1:]
                if possible_alias:
                    action_url = fti.queryMethodID(possible_alias,
                                                   default=action_url,
                                                   context=context)
        except AttributeError:
            # Don't raise if we don't have CMF 1.5
            pass

        return action_url
