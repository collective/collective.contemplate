import Globals

from Products.CMFDynamicViewFTI import fti

from collective.contemplate import typeinfo

class TemplateDynamicViewTypeInfo(typeinfo.TemplateTypeInfo,
                                  fti.DynamicViewTypeInformation):

    meta_type = 'TemplateDynamicViewTypeInfo'

Globals.InitializeClass(TemplateDynamicViewTypeInfo)
