# encoding: utf-8

# Copyright (C) 2013  Octavi Font <octavi.fs@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from icalendar import Calendar, Event
from datetime import datetime
import pytz

from django.conf import settings
# Don't import from __future__ import unicode_literals
# .add fails if the string has a special character [àáèéìí...]
# The result does not return a unicode string, but a binary string.


def generate(lessons):
    """
    Generates ical calendar (as a byte string) from an iterable of lessons
    (QuerySet, list...)
    """
    # Adjust the timezone, so the time is correctly displayed in GCalendar
    tz = pytz.timezone('Europe/Madrid')
    cal = Calendar()
    cal.add('prodid', '-//Calendari HorarisPompeu.com//mxm.dk//')
    cal.add('version', '2.0')
    # Give the calendar a name. I use this to remind the users where the
    # calendar comes from, in case they need a new one.
    cal.add('x-wr-calname', 'horarispompeu.com {}'.format(
        settings.ACADEMIC_YEAR))
    cal.add('x-wr-timezone', 'Europe/Madrid')
    for entry in lessons:
        event = Event()
        summary = "\n".join([entry.subject.name, entry.entry])
        event.add('summary', summary)
        event.add('location', entry.location)
        event.add('dtstart', tz.localize(entry.date_start))
        event.add('dtend', tz.localize(entry.date_end))
        event.add('dtstamp', datetime.now(tz))
        cal.add_component(event)
    return cal.to_ical()
