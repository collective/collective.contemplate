import Globals

from Products.CMFDynamicViewFTI import fti

from collective.contemplate import typeinfo

class TemplateDynamicViewTypeInfo(typeinfo.TemplateTypeInfo,
                                  fti.DynamicViewTypeInformation):
    """Template Dynamic View Type Information"""

    meta_type = 'TemplateDynamicViewTypeInfo'
    _properties = (fti.DynamicViewTypeInformation._properties +
                   typeinfo.TemplateTypeInfo._properties)

Globals.InitializeClass(TemplateDynamicViewTypeInfo)
