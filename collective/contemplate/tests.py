import unittest
from zope.testing import doctest

from Testing import ZopeTestCase
from Products.PloneTestCase import ptc
from Products.Five import zcml

from collective import contemplate

ptc.setupPloneSite()

optionflags = (doctest.NORMALIZE_WHITESPACE|
               doctest.ELLIPSIS|
               doctest.REPORT_NDIFF)

def setUp(test):
    zcml.load_config(package=contemplate, file='configure.zcml')

def test_suite():
    suite = ZopeTestCase.FunctionalDocFileSuite(
        'README.txt',
        optionflags=optionflags,
        setUp=setUp,
        test_class=ptc.FunctionalTestCase)
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
