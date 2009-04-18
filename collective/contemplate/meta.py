from zope import schema
from zope.publisher.interfaces import browser
from zope.app.publisher.browser import metadirectives
from Products.Five import metaclass
from Products.Five.browser import metaconfigure

from collective.contemplate import at

class IFormControllerPageDirective(metadirectives.IPageDirective):

    type_name = schema.TextLine(
        title=u"The name of the content type.",
        description=
        u"Used for the fallback when there is no template")

def formControllerPage(
    _context, name, permission, for_, type_name,
    layer=browser.IDefaultBrowserLayer, template=None, class_=None,
    allowed_interface=None, allowed_attributes=None,
    attribute='__call__', menu=None, title=None):
    """Add the name to the class dict to make it accessible for
    looking up the template"""
    class_name = 'GeneratedFormControllerTemplateAddForm'
    bases = (at.FormControllerTemplateAddForm,)
    if class_ is not None:
        class_name = class_.__name__
        bases = (class_, at.FormControllerTemplateAddForm)
    class_ = metaclass.makeClass(
        class_name, bases, dict(name=name, type_name=type_name))
    metaconfigure.page(
        _context, name, permission, for_, layer=layer,
        template=template, class_=class_,
        allowed_interface=allowed_interface,
        allowed_attributes=allowed_attributes, attribute=attribute,
        menu=menu, title=title)
