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
