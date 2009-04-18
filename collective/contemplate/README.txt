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
    >>> owner_browser.getLink(
    ...     url='createObject?type_name=Document').click()
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

A user with rights to administer templates may designate the page as a
template for the Page content type in that folder and below using
"Make template" in the actions menu.

    >>> owner_browser.getLink('Make template').click()
    >>> print owner_browser.contents
    <...
    ...Item designated as the template...

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
    'Foo Page Title'
    'Foo Template Description'
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
    ...     folder['foo-template-title'].absolute_url())
    >>> print owner_browser.contents
    <...
    ...Foo Template Title...
    ...Foo Template Description...

    >>> contributor_browser.open(
    ...     folder['foo-template-title'].absolute_url())
    Traceback (most recent call last):
    Unauthorized: ...

The template for a given content type may be replaced using the "Make
template" action on the new template.

    >>> owner_browser.open(folder['foo-page-title'].absolute_url())
    >>> owner_browser.getLink('Make template').click()
    >>> print owner_browser.contents
    <...
    ...Item designated as the template...

    >>> contributor_browser.open(folder.absolute_url())
    >>> contributor_browser.getLink(url='/+/addATDocument').click()
    >>> contributor_browser.getControl('Title').value
    'Foo Page Title'

The template may also be removed using the "Remove template" action on
the template based add form.

    >>> owner_browser.open(folder.absolute_url())
    >>> owner_browser.getLink(url='/+/addATDocument').click()
    >>> owner_browser.getLink('Remove template').click()
    >>> print owner_browser.contents
    <...
    ...Item removed as the template...
    >>> contributor_browser.url
    'http://nohost/plone/Members/foo-template-title'

    >>> contributor_browser.open(folder.absolute_url())
    >>> contributor_browser.getLink(
    ...     url='createObject?type_name=Document').click()
    >>> contributor_browser.url
    'http://nohost/plone/Members/test_user_1_/portal_factory/Document/document.../edit'
    >>> contributor_browser.getControl('Title').value
    ''
    >>> contributor_browser.getControl('Description').value
    ''
