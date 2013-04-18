# encoding: utf-8
from icalendar import Calendar, Event
from datetime import datetime
import pytz
# Don't import from __future__ import unicode_literals
# .add fails if the string has a special character [àáèéìí...]
# The result does not return a unicode string, but a binary string.


def generate(lessons):
    """
    Generates string with ical calendar from an iterable of lessons (QuerySet,
    list...)
    """
    tz = pytz.timezone('Europe/Madrid')
    cal = Calendar()
    cal.add('prodid', '-//Calendari HorarisPompeu.com//mxm.dk//')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'horarispompeu.com')
    cal.add('x-wr-timezone', 'Europe/Madrid')
    for entry in lessons:
        event = Event()
        summary = " ".join([entry.kind, entry.subgroup, entry.subject.name])
        event.add('summary', summary)
        event.add('dtstart', tz.localize(entry.date_start))
        event.add('dtend', tz.localize(entry.date_end))
        event.add('dtstamp', datetime.now(tz))
        event.add('location', entry.room)
        cal.add_component(event)
    return cal.to_ical()
