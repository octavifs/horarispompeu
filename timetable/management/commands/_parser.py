#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals
from bs4 import BeautifulSoup
from datetime import date, time, datetime
from pytz import timezone
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

    def __str__(self):
        rep = "<Lesson object>\n"
        rep += "subject: " + repr(self.subject) + "\n"
        rep += "kind: " + repr(self.kind) + "\n"
        rep += "group: " + repr(self.group) + "\n"
        rep += "room: " + repr(self.room) + "\n"
        rep += "date_start: " + repr(self.date_start) + "\n"
        rep += "date_end: " + repr(self.date_end) + "\n"
        return rep

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
    tz = timezone('Europe/Madrid')
    hours_str = text.strip().replace('.', ':').split("-")
    h_init_list = [int(data) for data in hours_str[0].split(":")]
    h_end_list = [int(data) for data in hours_str[1].split(":")]
    h_init = time(*h_init_list, tzinfo=tz)
    h_end = time(*h_end_list, tzinfo=tz)
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
