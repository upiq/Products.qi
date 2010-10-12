from zope import schema
from Products.qi import MessageFactory as _
from Products.CMFDynamicViewFTI.interface import ISelectableBrowserDefault

class IChart(ISelectableBrowserDefault):
    title=schema.TextLine(title=_(u"Title"),
                        description=_("Name of this digital report"),
                        required=True)
    description=schema.Text(title=_(u"Description"),
                            description=_(u"A description of the information shown by this report"),
                            required=True)
    """startdate=schema.Date(title=_(u"Start Date"),
                            description=_(u"The begining of the period reported by this page, leave blank to show earliest data"),
                            required=False)
    enddate=schema.Date(title=_(u"End Date"),
                            description=_(u"The end of the period reported by this page, leave blank to to show current data"),
                            required=False)"""
    startdate =  schema.Choice(
        title=u"Start Date",
        description=u"The earliest date that will be shown by this chart",
        vocabulary="qi.vocab.ChartDates",
        required=False)
    enddate =  schema.Choice(
        title=u"End Date",
        description=u"The latest date that will be shown by this chart",
        vocabulary="qi.vocab.ChartDates",
        required=False)
    
    measures=schema.Set(title=_(u"Measures"),
                            description=_(u"The measures shown on this report"),
                            value_type=schema.Choice(title=_("Measure ID"),
                                                    vocabulary="qi.vocab.Measures"),
                            required=True)
    derived=schema.Set(title=_(u"Calculated Measures"),
                            description=_(u"The calculated measures shown on this report"),
                            value_type=schema.Choice(title=_("Name"),
                                                    vocabulary="qi.vocab.DerivedMeasures"),
                            required=True)

    teams=schema.Set(title=_(u"Teams"),
                            description=_(u"The teams shown on this report"),
                            value_type=schema.Choice(title=_("Team ID"),
                                                    vocabulary="qi.vocab.Teams"),
                            required=True)

IQIChart=IChart