from collective.testcaselayer import ptc as tcl_ptc
from collective.testcaselayer import common

from collective import contemplate


class Layer(tcl_ptc.BasePTCLayer):
    """Install collective.contemplate"""

    def afterSetUp(self):
        self.loadZCML('testing.zcml', package=contemplate)
        self.addProfile('collective.contemplate:default')

layer = Layer([common.common_layer])


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
