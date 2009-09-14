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

    def addContent(self, container, type_name, id_,
                   **kw):
        content = container[
            container.invokeFactory(type_name=type_name, id=id_)]
        content.processForm(values=kw)
        return content

    def afterSetUp(self):
        self.login()
        self.addContent(
            self.folder,
            type_name='Document', id_='foo-document-title',
            title='Foo Document Title',
            description='Foo document description')
        self.addContent(
            self.folder, type_name='Document',
            id_='bar-document-title', title='Bar Document Title',
            description='Bar document description')
        self.addContent(
            self.folder, type_name='Event', id_='qux-event-title',
            title='Qux Event Title',
            description='Qux event description')
        self.logout()

batch_layer = BatchLayer([layer])
