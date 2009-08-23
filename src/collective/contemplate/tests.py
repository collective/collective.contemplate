import unittest
from zope.testing import doctest

from Testing import ZopeTestCase
from Products.PloneTestCase import ptc

from collective.testcaselayer import ptc as tcl_ptc

from collective.contemplate import testing

optionflags = (doctest.NORMALIZE_WHITESPACE|
               doctest.ELLIPSIS|
               doctest.REPORT_NDIFF)

def test_suite():
    ptc_suite = ZopeTestCase.FunctionalDocFileSuite(
        'compatible.txt',
        optionflags=optionflags,
        test_class=ptc.FunctionalTestCase)
    ptc_suite.layer = tcl_ptc.ptc_layer

    contemplate_suite = ZopeTestCase.FunctionalDocFileSuite(
        'README.txt',
        optionflags=optionflags,
        test_class=ptc.FunctionalTestCase)
    contemplate_suite.layer = testing.layer

    return unittest.TestSuite([ptc_suite, contemplate_suite])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
