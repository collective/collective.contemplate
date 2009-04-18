import unittest
from zope.testing import doctest

from Testing import ZopeTestCase
from Products.PloneTestCase import ptc

ptc.setupPloneSite()

optionflags = (doctest.NORMALIZE_WHITESPACE|
               doctest.ELLIPSIS|
               doctest.REPORT_NDIFF)

def test_suite():
    suite = ZopeTestCase.FunctionalDocFileSuite(
        'README.txt',
        optionflags=optionflags,
        test_class=ptc.FunctionalTestCase)
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
