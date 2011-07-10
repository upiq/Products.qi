from zope.interface import Interface


class IQIProductLayer(Interface):
    """
    Marker interface for browser layers isolated to this
    product/package installed within a Plone site.
    Should be used in conjunction with plone.browserlayer
    declared as dependency in Products.qi setup.py and via
    GenericSetup profile xml.
    """

