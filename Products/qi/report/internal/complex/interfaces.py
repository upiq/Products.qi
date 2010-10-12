from zope import schema
from Products.qi import MessageFactory as _
from Products.CMFDynamicViewFTI.interface import ISelectableBrowserDefault

class IChartHolder(ISelectableBrowserDefault):
    title=schema.TextLine(title=_(u"Title"),
                            description=_(u"Report Title"),
                            required=True
                            )
    description=schema.Text(title=_(u"Description"),
                            description=_(u"Report Description"),
                            required=True
                            )
    perseverate=schema.Bool(title=_(u"Perseverate"),
                                description=_(u"If data is missing, present previous month's data instead"),
                            )