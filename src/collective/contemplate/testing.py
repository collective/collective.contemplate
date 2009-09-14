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

class BatchLayer(tcl_ptc.BasePTCLayer):
    """Add some content for batch editing"""

    def afterSetUp(self):
        self.login()
        self.folder.invokeFactory(
            type_name='Document', id='foo-document-title',
            title='Foo Document Title',
            description='Foo document description')
        self.folder.invokeFactory(
            type_name='Document', id='bar-document-title',
            title='Bar Document Title',
            description='Bar document description')
        self.folder.invokeFactory(
            type_name='Event', id='qux-event-title',
            title='Qux Event Title',
            description='Qux event description')
        self.logout()

batch_layer = BatchLayer([layer])
