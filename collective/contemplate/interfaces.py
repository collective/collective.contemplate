from zope import interface

class ITemplate(interface.Interface):
    """A content template"""

class ITemplateForm(interface.Interface):
    """A content template"""

    name = interface.Attribute('Name')
