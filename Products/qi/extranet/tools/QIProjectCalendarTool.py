import re
import Products.CMFPlone.CalendarTool as BaseModule

import calendar

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from zope.interface import implements
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import UniqueObject

from Products.CMFCalendar.interfaces import ICalendarTool
from Products.CMFCalendar.permissions import ManagePortal

#override the two values we care about
class QICalendarTool(BaseModule.CalendarTool):
    def getEventsForCalendar(self, month='1', year='2002', **kw):
        """ recreates a sequence of weeks, by days each day is a mapping.
            {'day': #, 'url': None}
        """
        year = int(year)
        month = int(month)
        # daysByWeek is a list of days inside a list of weeks, like so:
        # [[0, 1, 2, 3, 4, 5, 6],
        #  [7, 8, 9, 10, 11, 12, 13],
        #  [14, 15, 16, 17, 18, 19, 20],
        #  [21, 22, 23, 24, 25, 26, 27],
        #  [28, 29, 30, 31, 0, 0, 0]]
        daysByWeek = self._getCalendar().monthcalendar(year, month)
        weeks = []
        
        project = kw.get('project', None)
        events = self.catalog_getevents(year, month, project)

        for week in daysByWeek:
            days = []
            for day in week:
                if events.has_key(day):
                    days.append(events[day])
                else:
                    days.append({'day': day, 'event': 0, 'eventslist':[]})

            weeks.append(days)

        return weeks

    def catalog_getevents(self, year, month,project=None):
        """ given a year and month return a list of days that have events 
        """
        
        
        # XXX: this method violates the rules for tools/utilities:
        # it depends on a non-utility tool
        year = int(year)
        month = int(month)
        last_day = self._getCalendar().monthrange(year, month)[1]
        first_date = self.getBeginAndEndTimes(1, month, year)[0]
        last_date = self.getBeginAndEndTimes(last_day, month, year)[1]

        ctool = getToolByName(self, 'portal_catalog')
        #review_state=None
        #if not project:
        review_state=self.getCalendarStates()
        if project:
            oldstates=[k for k in review_state]
            oldstates.append('private')
            review_state=oldstates
        query = ctool(
                        portal_type=self.getCalendarTypes(),
                        review_state=review_state,
                        start={'query': last_date, 'range': 'max'},
                        end={'query': first_date, 'range': 'min'},
                        sort_on='start' )

        # compile a list of the days that have events
        eventDays={}
        for daynumber in range(1, 32): # 1 to 31
            eventDays[daynumber] = {'eventslist': [],
                                    'event': 0,
                                    'day': daynumber}
        includedevents = []
        for result in query:
            
            if hasattr(result.getObject(),'getProject'):
                eventproject=result.getObject().getProject()
            else:
                eventproject=None
            
            #skip this result
            if project and eventproject!=project:
                continue
            if result.getRID() in includedevents:
                break
            else:
                includedevents.append(result.getRID())
            event={}
            # we need to deal with events that end next month
            if  result.end.month() != month:
                # doesn't work for events that last ~12 months
                # fix it if it's a problem, otherwise ignore
                eventEndDay = last_day
                event['end'] = None
            else:
                eventEndDay = result.end.day()
                event['end'] = result.end.Time()
            # and events that started last month
            if result.start.month() != month:  # same as above (12 month thing)
                eventStartDay = 1
                event['start'] = None
            else:
                eventStartDay = result.start.day()
                event['start'] = result.start.Time()

            event['title'] = result.Title or result.getId

            if eventStartDay != eventEndDay:
                allEventDays = range(eventStartDay, eventEndDay+1)
                eventDays[eventStartDay]['eventslist'].append(
                        {'end': None,
                         'start': result.start.Time(),
                         'title': event['title']} )
                eventDays[eventStartDay]['event'] = 1

                for eventday in allEventDays[1:-1]:
                    eventDays[eventday]['eventslist'].append(
                        {'end': None,
                         'start': None,
                         'title': event['title']} )
                    eventDays[eventday]['event'] = 1

                if result.end == result.end.earliestTime():
                    last_day_data = eventDays[allEventDays[-2]]
                    last_days_event = last_day_data['eventslist'][-1]
                    last_days_event['end'] = (result.end-1).latestTime().Time()
                else:
                    eventDays[eventEndDay]['eventslist'].append( 
                        { 'end': result.end.Time()
                        , 'start': None, 'title': event['title']} )
                    eventDays[eventEndDay]['event'] = 1
            else:
                eventDays[eventStartDay]['eventslist'].append(event)
                eventDays[eventStartDay]['event'] = 1
            # This list is not uniqued and isn't sorted
            # uniquing and sorting only wastes time
            # and in this example we don't need to because
            # later we are going to do an 'if 2 in eventDays'
            # so the order is not important.
            # example:  [23, 28, 29, 30, 31, 23]
        return eventDays
