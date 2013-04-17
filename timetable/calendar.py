# encoding: utf-8
from icalendar import Calendar, Event
# Don't import from __future__ import unicode_literals
# .add fails if the string has a special character [àáèéìí...]
# The result does not return a unicode string, but a binary string.


def generate(lessons):
    """
    Generates string with ical calendar from an iterable of lessons (QuerySet,
    list...)
    """
    cal = Calendar()
    cal.add('prodid', '-//Calendari HorarisPompeu.com//mxm.dk//')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'horarispompeu.com')

    for entry in lessons:
        event = Event()
        summary = " ".join([entry.kind, entry.subgroup, entry.subject.name])
        event.add('summary', summary)
        event.add('dtstart', entry.date_start)
        event.add('dtend', entry.date_end)
        event.add('location', entry.room)
        cal.add_component(event)
    return cal.to_ical()

def regenerate(calendar):
    """
    Redoes a calendar
    """
    # Select lessons. Maybe we could do this in DegreeSubject object, as a custom query already
    lessons = []
    # Regenerate calendar
    return generate(lessons)

