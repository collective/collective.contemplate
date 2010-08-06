from zope import component

from Acquisition import aq_inner

from collective.contemplate import interfaces


class TemplateAddForm(object):

    def __init__(self, *args, **kw):
        super(TemplateAddForm, self).__init__(*args, **kw)
        self.form_context = aq_inner(self.context)

    def update(self, *args, **kw):
        self.updateTemplate(aq_inner(self.form_context.context))

    def updateTemplate(self, context):
        self.template = None
        info = interfaces.ITemplateTypeInfo(
            context.portal_types.getTypeInfo(self.type_name), None)
        if info is not None:
            self.template = template = info.getTemplate(context)
            if template is not None:
                self.context = template

    def createAndAdd(self, data):
        """Delegate to the type info"""
        destination = aq_inner(self.form_context.context)
        if 'id' not in data:
            data['id'] = None
        new_id = destination.invokeFactory(
            type_name=self.type_name, **data)
        return destination[new_id]

    def nextURL(self):
        return str(component.getMultiAdapter(
            (self.added, self.request), name=u"absolute_url"))
