from Acquisition import aq_inner

from Products.statusmessages import interfaces as status_ifaces

from collective.contemplate import form
from collective.contemplate import at

class BatchEditForm(at.FormControllerTemplateAddForm):

    def __init__(self, *args, **kw):
        super(form.TemplateAddForm, self).__init__(*args, **kw)
        self.form_context = context = aq_inner(self.context)

        portal_catalog = context.portal_catalog
        paths = self.request['paths']
        type_name = portal_catalog._catalog[
            portal_catalog.getrid(paths[0])].portal_type
        self.error = False
        for path in paths[1:]:
            if type_name != portal_catalog._catalog[
                portal_catalog.getrid(path)].portal_type:
                self.error = True
                self.status = (
                    'Selected items are not of the same type')
        self.type_name = type_name
            
        self.updateTemplate(context)

    def __call__(self):
        if self.error:
            context = aq_inner(self.form_context)
            status_ifaces.IStatusMessage(
                self.request).addStatusMessage(
                self.status, type='error')
            self.request.response.redirect(
                context.absolute_url()+'/folder_contents')
            return ''
        return super(BatchEditForm, self).__call__()

    def finish(self, controller_state, edit_action):
        context = aq_inner(self.form_context)

        for key in self.request.form.keys():
            if key.startswith('form.button.'):
                self.request.form[
                    key+'.batch'] = self.request.form.pop(key)

        for path in self.request['paths']:
            self.request.form.setdefault('form.submitted', 1)
            obj = context.restrictedTraverse(path)
            self.maybePopId(obj)
            edit_action = self.getEdit(obj)
            self.mapply(obj.restrictedTraverse(edit_action))

        self.request.response.redirect(
            context.absolute_url()+'/folder_contents')
        return ''

class BatchNullView(object):
    pass
