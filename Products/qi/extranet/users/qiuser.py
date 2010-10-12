from plone.app.vocabularies.users import UsersSource
import itertools
from zope.interface import implements, classProvides
from zope.schema.interfaces import ISource, IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm

from zope.app.form.browser.interfaces import ISourceQueryView, ITerms
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName


class QiUsersSource(UsersSource):
    implements(ISource)
    classProvides(IContextSourceBinder)
    #behave just like a the normal object




    def search(self, query):
        names=[u['userid'] for u in self.users.searchUsers(fullname=query)]
        alluserids={}
        for name in names:
            alluserids[name]=name
        emails=[u['userid'] for u in self.users.searchUsers(login=query)]
        for name in emails:
            alluserids[name]=name
        return alluserids.keys()