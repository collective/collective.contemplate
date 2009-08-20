.. -*-doctest-*-

=================
Content Templates
=================

Open a browser and log in as a user who is allowed to administer
templates.

    >>> from Products.Five.testbrowser import Browser
    >>> from Products.PloneTestCase import ptc
    >>> owner_browser = Browser()
    >>> owner_browser.handleErrors = False
    >>> owner_browser.open(portal.absolute_url())
    >>> owner_browser.getLink('Log in').click()
    >>> owner_browser.getControl(
    ...     'Login Name').value = ptc.portal_owner
    >>> owner_browser.getControl(
    ...     'Password').value = ptc.default_password
    >>> owner_browser.getControl('Log in').click()

Before we've added a template, adding content proceeds as before with
fields empty.

    >>> owner_browser.open(portal.Members.absolute_url())
    >>> owner_browser.getLink(url='/+/addATDocument').click()
    >>> owner_browser.url
    'http://nohost/plone/Members/portal_factory/Document/document.../edit'
    >>> owner_browser.getControl('Title').value
    ''
    >>> owner_browser.getControl('Description').value
    ''

Finish creating the page to use as a template.

    >>> owner_browser.getControl('Title').value = 'Foo Template Title'
    >>> owner_browser.getControl(
    ...     'Description').value = 'Foo Template Description'
    >>> owner_browser.getControl('Save').click()
    >>> print owner_browser.contents
    <...
    ...Changes saved...
    ...Foo Template Title...
    ...Foo Template Description...

Make sure the template is visible to users that will use it as a
template.

    >>> self.loginAsPortalOwner()
    >>> portal.portal_workflow.doActionFor(
    ...     portal.Members['foo-template-title'], 'publish')
    >>> self.logout()

A user with rights to administer templates may designate the page as a
template for the Page content type in that folder and below using
"Make template" in the actions menu.

TODO    >>> owner_browser.getLink('Make template').click()
TODO    >>> print owner_browser.contents
TODO    <...
TODO    ...Item designated as the template...

    >>> portal.Members.addReference(
    ...     portal.Members['foo-template-title'],
    ...     relationship='contemplate.Document')
    <Reference sid:... tid:... rel:contemplate.Document>

Open another browser and log in as a normal user.

    >>> from Products.Five.testbrowser import Browser
    >>> from Products.PloneTestCase import ptc
    >>> contributor_browser = Browser()
    >>> contributor_browser.handleErrors = False
    >>> contributor_browser.open(portal.absolute_url())
    >>> contributor_browser.getLink('Log in').click()
    >>> contributor_browser.getControl(
    ...     'Login Name').value = ptc.default_user
    >>> contributor_browser.getControl(
    ...     'Password').value = ptc.default_password
    >>> contributor_browser.getControl('Log in').click()

Once a template has been designated, adding an item of the same
content type in that folder or below will use the template.

    >>> contributor_browser.open(folder.absolute_url())
    >>> contributor_browser.getLink(url='/+/addATDocument').click()
    >>> contributor_browser.getControl('Title').value
    'Foo Template Title'
    >>> contributor_browser.getControl('Description').value
    'Foo Template Description'

The edit page will be rendered and validated against the template
without copying or otherwise instantiating new content.

    >>> contributor_browser.getControl('Title').value = ''
    >>> contributor_browser.getControl('Save').click()
    >>> print contributor_browser.contents
    <...
    ...Please correct the indicated errors...
    ...Title is required...
    >>> contributor_browser.url
    'http://nohost/plone/Members/test_user_1_/+/addATDocument'
    >>> portal.Members.contentValues()
    [<ATDocument at /plone/Members/foo-template-title>,
     <ATFolder at /plone/Members/test_user_1_>]
    >>> folder.contentValues()
    []

Successfully saving the form will copy the template and modify it with
the submitted form data.

    >>> contributor_browser.getControl('Title').value = 'Foo Page Title'
    >>> contributor_browser.getControl('Save').click()
    >>> contributor_browser.url
    'http://nohost/plone/Members/test_user_1_/foo-page-title'
    >>> print contributor_browser.contents
    <...
    ...Changes saved...
    Foo Page Title...
    Foo Template Description...
    >>> portal.Members.contentValues()
    [<ATDocument at /plone/Members/foo-template-title>,
     <ATFolder at /plone/Members/test_user_1_>]
    >>> folder.contentValues()
    [<ATDocument at /plone/Members/test_user_1_/foo-page-title>]

The content added from the template behaves as other content and is
editable by the owner.

    >>> contributor_browser.getLink('Edit')
    <Link text='Edit' url='http://nohost/plone/Members/test_user_1_/foo-page-title/edit'>

A user without rights to administer templates may not designate
content as a template.

    >>> contributor_browser.getLink('Make template')
    Traceback (most recent call last):
    LinkNotFoundError

The template's permissions and field values have not been changed.

    >>> owner_browser.open(
    ...     portal.Members['foo-template-title'].absolute_url())
    >>> print owner_browser.contents
    <...
    ...Foo Template Title...
    ...Foo Template Description...

    >>> contributor_browser.open(
    ...     portal.Members['foo-template-title'].absolute_url())
    >>> contributor_browser.getLink('Edit')
    Traceback (most recent call last):
    LinkNotFoundError

The template for a given content type may be replaced using the "Make
template" action on the new template.

TODO    >>> owner_browser.open(folder['foo-page-title'].absolute_url())
TODO    >>> owner_browser.getLink('Make template').click()
TODO    >>> print owner_browser.contents
TODO    <...
TODO    ...Item designated as the template...

    >>> portal.Members.deleteReference(
    ...     portal.Members['foo-template-title'],
    ...     relationship='contemplate.Document')
    >>> portal.Members.addReference(
    ...     folder['foo-page-title'],
    ...     relationship='contemplate.Document')
    <Reference sid:... tid:... rel:contemplate.Document>

    >>> contributor_browser.open(folder.absolute_url())
    >>> contributor_browser.getLink(url='/+/addATDocument').click()
    >>> contributor_browser.getControl('Title').value
    'Foo Page Title'

The template may also be removed using the "Remove template" action on
the template based add form.

TODO    >>> owner_browser.open(folder.absolute_url())
TODO    >>> owner_browser.getLink(url='/+/addATDocument').click()
TODO    >>> owner_browser.getLink('Remove template').click()
TODO    >>> print owner_browser.contents
TODO    <...
TODO    ...Item removed as the template...
TODO    >>> contributor_browser.url
TODO    'http://nohost/plone/Members/foo-template-title'

    >>> portal.Members.deleteReference(
    ...     folder['foo-page-title'],
    ...     relationship='contemplate.Document')

    >>> contributor_browser.open(folder.absolute_url())
    >>> contributor_browser.getLink(url='/+/addATDocument').click()
    >>> contributor_browser.url
    'http://nohost/plone/Members/test_user_1_/portal_factory/Document/document.../edit'
    >>> contributor_browser.getControl('Title').value
    ''
    >>> contributor_browser.getControl('Description').value
    ''

Global Templates
================

A template can be designated as the global template for a given portal
type.  To do so set, the "Global Template UID" property of the type
info in the portal_types tool to the UID of the template object.

Create an event as the template.

    >>> self.loginAsPortalOwner()
    >>> foo_event = portal[portal.invokeFactory(
    ...     type_name='Event', id='event-template-title',
    ...     title='Event Template Title',
    ...     description='Event template description')]

Set the type info property to the UID for the event template.

    >>> portal.portal_types.Event.manage_changeProperties(
    ...     global_uid=foo_event.UID())

Now when an event is added through the browser, it will be created
from the template.

    >>> contributor_browser.open(folder.absolute_url())
    >>> contributor_browser.getLink(url='/+/addATEvent').click()
    >>> contributor_browser.getControl('Title').value
    'Event Template Title'
    >>> contributor_browser.getControl('Description').value
    'Event template description'

Reserved IDs
============

A reserved_id property can be set on a type information.  If set and
an object with that ID already exists, then the type is not allowed to
be added.

    >>> self.login()
    >>> folder.allowedContentTypes()
    [<TemplateDynamicViewTypeInfo at /plone/portal_types/Document>,
     <TemplateDynamicViewTypeInfo at /plone/portal_types/Event>,
     <TemplateDynamicViewTypeInfo at /plone/portal_types/Favorite>,
     <TemplateDynamicViewTypeInfo at /plone/portal_types/File>,
     <TemplateDynamicViewTypeInfo at /plone/portal_types/Folder>,
     <TemplateDynamicViewTypeInfo at /plone/portal_types/Image>,
     <TemplateDynamicViewTypeInfo at /plone/portal_types/Link>,
     <TemplateDynamicViewTypeInfo at /plone/portal_types/News Item>]
    >>> portal.portal_types.Document.reserved_id = 'foo-page-title'
    >>> folder.allowedContentTypes()
    [<TemplateDynamicViewTypeInfo at /plone/portal_types/Event>,
     <TemplateDynamicViewTypeInfo at /plone/portal_types/Favorite>,
     <TemplateDynamicViewTypeInfo at /plone/portal_types/File>,
     <TemplateDynamicViewTypeInfo at /plone/portal_types/Folder>,
     <TemplateDynamicViewTypeInfo at /plone/portal_types/Image>,
     <TemplateDynamicViewTypeInfo at /plone/portal_types/Link>,
     <TemplateDynamicViewTypeInfo at /plone/portal_types/News Item>]
