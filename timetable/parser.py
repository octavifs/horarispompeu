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
import copy
import re
import itertools


class Lesson(object):
    def __init__(self,
                 subject=None,
                 kind=None,
                 group=None,
                 room=None,
                 date_start=None,
                 date_end=None,
                 raw_data=None):
        self.subject = subject
        self.kind = kind
        self.group = group
        self.room = room
        self.date_start = date_start
        self.date_end = date_end
        self.raw_data = raw_data

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
        rep += "raw_data: " + repr(self.raw_data)
        return rep

    def __repr__(self):
        return self.__str__()

    def copy(self):
        return copy.deepcopy(self)

#########################################################
# Regular expressions needed to parse the ESUP calendar #
#########################################################
# See tests for details on what is or isn't parsed.

# Format (aprox): HH:mm - HH:mm
regexp_date = re.compile(r'^(\d{1,2})\D+(\d{1,2})\D+(\d{1,2})\D+(\d{1,2})\D*')
# Format (aprox): group: {room or rooms}
regexp_room = re.compile(r'^\w+:\s*(.+)$')
# Format (aprox): {Letter}{Number}: {room or rooms}
regexp_group = re.compile(r'^([a-zA-Z]\d+[a-zA-Z]?):\s*.+$')


def parsedays(row):
    """
    Parses an html row from an esup calendar and returns a list of dates with
    the day of each cell of the row.
    """
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
    """
    Parses a text using regexp_date and obtains an initial and final hour for
    an event.
    """
    hours = [int(h) for h in regexp_date.match(text.strip()).groups()]
    h_init = time(hours[0], hours[1])
    h_end = time(hours[2], hours[3])
    return (h_init, h_end)


def parselesson(text, h_init, h_end, day):
    """
    Generator that receives a string (from the html calendar) and yields as many
    lessons as the cell contains.
    If the parser can't fully process the entry, it will be yielded anyway,
    although some of the content may be missing.
    """
    raw_data = text.strip()
    # Divide input by lessons, if more than 1 are found per cell
    lessons = [lesson.strip() for lesson in re.split(r'----+', raw_data)]
    for lesson in lessons:
        # Divide input by lines. Also clear any unnecesary spaces or blank lines
        lines = [line.strip() for line in lesson.splitlines() if line.strip()]
        # If we have less than 3 lines, that means that there is no class
        # Generally, we would find one of the following messages:
        # - Festiu
        # - Subject\n NO HI HA CLASSE
        # So the best course of action is ignoring the iteration
        if len(lines) < 3:
            continue
        # Prepare a lesson
        c = Lesson(
            raw_data=raw_data,
            subject=lines[0],
            kind=lines[1],
            date_start=datetime.combine(day, h_init),
            date_end=datetime.combine(day, h_end)
        )
        for l in lines[2:]:
            # Update hour if necessary
            if regexp_date.match(l):
                parsed_date = parsehours(l)
                c.date_start = datetime.combine(day, parsed_date[0])
                c.date_end = datetime.combine(day, parsed_date[1])
            # Yield a lesson for each group
            else:
                match_room = regexp_room.match(l)
                match_group = regexp_group.match(l)
                c.room = match_room.groups()[0] if match_room else None
                c.group = match_group.groups()[0] if match_group else None
                yield c.copy()


def parse(html):
    """
    Returns an iterable with a list of Lesson objects. The lessons returned may
    not be complete, since the parser can't deal with all the possible cases.
    """
    lessons = itertools.chain()
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
                data = cell.get_text().strip()
                if numcell == 0:
                    h_init, h_end = parsehours(data)
                else:
                    day = days[numcell]
                    lessons = itertools.chain(lessons, parselesson(data, h_init, h_end, day))
    return lessons
