#!/usr/bin/env python
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

from __future__ import unicode_literals
from bs4 import BeautifulSoup
from datetime import date, time, datetime
from icalendar import Calendar, Event
from StringIO import StringIO
import copy
import re


class Lesson(object):
    subject = ""
    kind = ""
    group = ""
    room = ""
    date_start = ""
    date_end = ""
    raw_data = ""

    def __key(self):
        return (self.subject, self.kind, self.group, self.room, self.date_start, self.date_end)

    def __hash__(self):
        # As suggested in: http://stackoverflow.com/a/2909119
        return hash(self.__key())

    def __eq__(self, other):
        if type(other) is type(self):
            return other.__key() == self.__key()
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        rep = "<Lesson object>\n"
        rep += "subject: " + repr(self.subject) + "\n"
        rep += "kind: " + repr(self.kind) + "\n"
        rep += "group: " + repr(self.group) + "\n"
        rep += "room: " + repr(self.room) + "\n"
        rep += "date_start: " + repr(self.date_start) + "\n"
        rep += "date_end: " + repr(self.date_end) + "\n"
        #return rep
        return self.raw_data

    def __repr__(self):
        return self.raw_data

    def copy(self):
        return copy.deepcopy(self)


def parsedays(row):
    days = []
    for numcell, cell in enumerate(row.find_all("td")):
        if numcell == 0:
            days.append(None)
            continue
        day_list = [int(data) for data in cell.get_text().split("/")]
        day_list.reverse()
        day = date(*day_list)
        days.append(day)
    return days


def parsehours(text):
    hours_str = text.strip().replace('.', ':').split("-")
    h_init_list = [int(data) for data in hours_str[0].split(":")]
    h_end_list = [int(data) for data in hours_str[1].split(":")]
    h_init = time(*h_init_list)
    h_end = time(*h_end_list)
    return h_init, h_end


def parselesson(cell, h_init, h_end, day):
    lessons = []
    buf = StringIO(cell.get_text().strip())
    c = Lesson()
    c.raw_data = cell.get_text().strip()
    # This finds any string followed by :, any number of spaces and
    # 2 digits separated by a point. The second digit might be preceded by any number of letters.
    group_regex = re.compile(r"(\w+\s*\w*):?\s+(\d{2}[\.|\,]\w*\d+)")
    for line in buf:
        line = line.strip()
        while line == "":
            line = buf.readline().strip()
        c.subject = line
        for line in buf:
            line = line.strip()
            c.kind = line
            if c.kind != "":
                break
        c.date_start = datetime.combine(day, h_init)
        c.date_end = datetime.combine(day, h_end)
        for line in buf:
            line = line.strip()
            if "----------------" in line:
                break
            if line == "":
                continue
            if " - " in line:
                h_init, h_end = parsehours(line)
                c.date_start = datetime.combine(day, h_init)
                c.date_end = datetime.combine(day, h_end)
                continue
            g = group_regex.match(line)
            if g is not None:
                group = g.groups()[0]
                room = g.groups()[1]
                if "aula" in group.lower():
                    group = ""
                c.group = group
                c.room = room
                lessons.append(c)
                c = c.copy()
    return lessons


def createcalendar(lessons):
    cal = Calendar()
    cal.add('prodid', '-//My calendar product//mxm.dk//')
    cal.add('version', '2.0')

    for entry in lessons:
        event = Event()
        summary = u" ".join([entry.subject, entry.kind, entry.group])
        event.add('summary', summary)
        event.add('dtstart', entry.date_start)
        event.add('dtend', entry.date_end)
        event.add('location', entry.room)
        cal.add_component(event)
    f = open('example.ics', 'wb')
    f.write(cal.to_ical())
    f.close()

    pass


def parse(html):
    lessons = []
    soup = BeautifulSoup(html)
    for table in soup.find_all("table"):
        for numrow, row in enumerate(table.find_all("tr")):
            if numrow == 0:
                continue
            if numrow == 1:
                days = parsedays(row)
                continue
            h_init = None
            h_end = None
            for numcell, cell in enumerate(row.find_all("td")):
                if numcell == 0:
                    h_init, h_end = parsehours(cell.get_text().strip())
                else:
                    day = days[numcell]
                    lessons.extend(parselesson(cell, h_init, h_end, day))
    return lessons
