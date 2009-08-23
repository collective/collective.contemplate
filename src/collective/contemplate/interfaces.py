from zope import interface
from zope.component import interfaces

class ITemplate(interface.Interface):
    """A content template"""

class ITemplateTypeInfo(interface.Interface):
    """Content template type information"""

    name = interface.Attribute('Name')

class ITemplateCopiedEvent(interfaces.IObjectEvent):
    """Content has been added using a template"""

class TemplateCopiedEvent(interfaces.ObjectEvent):
    """Content has been added using a template"""
    interface.implements(ITemplateCopiedEvent)

    def __init__(self, object, template):
        super(TemplateCopiedEvent, self).__init__(object)
        self.template = template

class IContainerOnlyTemplate(interface.Interface):
    """Template only used for the assigned container"""
