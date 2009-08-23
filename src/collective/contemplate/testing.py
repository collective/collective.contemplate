from Products.Five import zcml

from collective.testcaselayer import ptc as tcl_ptc

from collective import contemplate

class Layer(tcl_ptc.BasePTCLayer):
    """Install collective.contemplate"""

    def afterSetUp(self):
        # Don't ignore exceptions
        error_props = self.portal.error_log.getProperties()
        error_props['ignored_exceptions'] = ()
        error_props = self.portal.error_log.setProperties(
            **error_props)

        zcml.load_config(package=contemplate, file='configure.zcml')
        self.addProfile('collective.contemplate:default')

layer = Layer([tcl_ptc.ptc_layer])
