from zope import component

import Acquisition

from collective.contemplate import interfaces

class TemplateAddForm(object):

    def __init__(self, *args, **kw):
        super(TemplateAddForm, self).__init__(*args, **kw)
        self.adding = self.context
        self.template = None
        info = interfaces.ITemplateTypeInfo(
            self.adding.context.portal_types.getTypeInfo(
                self.type_name), None)
        if info is not None:
            self.template = info.getTemplate(
                Acquisition.aq_inner(self.adding.context))
            if self.template is not None:
                self.context = self.template

    def createAndAdd(self, data):
        """Delegate to the type info"""
        destination = Acquisition.aq_inner(self.adding.context)
        if 'id' not in data:
            data['id'] = None
        new_id = destination.invokeFactory(
            type_name=self.type_name, **data)
        return destination[new_id]
        
    def nextURL(self):
        return str(component.getMultiAdapter(
            (self.added, self.request), name=u"absolute_url"))
