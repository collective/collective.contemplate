from Products.Five import zcml

from collective.testcaselayer import ptc as tcl_ptc

from collective import contemplate

class Layer(tcl_ptc.BasePTCLayer):
    """Install collective.contemplate"""

    def afterSetUp(self):
        zcml.load_config(package=contemplate, file='configure.zcml')
        self.addProfile('collective.contemplate:default')

layer = Layer([tcl_ptc.ptc_layer])
