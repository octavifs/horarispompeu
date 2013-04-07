# encoding: utf-8
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from __future__ import unicode_literals
from django.test import TestCase
from django.db import IntegrityError
from timetable.models import *
import datetime
from icalendar import Calendar, Event


class DatabaseDuplicateTests(TestCase):
    """
    Tests that insertion of duplicates in the DB model raises IntegrityError
    exception.
    """
    def setUp(self):
        """
        Populates the mockup test database with some test data
        """
        # Create test data
        self.faculty = Faculty(name="ESUP")
        self.faculty.save()
        self.subject = Subject(
            faculty=self.faculty,
            name="Àlgebra"
        )
        self.subject.save()
        self.academic_year = AcademicYear(year="2012-13")
        self.academic_year.save()
        self.lesson = Lesson(
            subject=self.subject,
            group="GRUP 1",
            subgroup="",
            kind="TEORIA",
            room="52.349",
            date_start=datetime.datetime(2013, 4, 4, 10, 30, 00),
            date_end=datetime.datetime(2013, 4, 4, 12, 30, 00),
            academic_year=self.academic_year,
            raw_entry="Some stuff"
        )
        self.lesson.save()
        self.degree = Degree(
            faculty=self.faculty,
            name="Grau en Enginyeria de Sistemes Audiovisuals"
        )
        self.degree.save()
        self.degreesubject = DegreeSubject(
            subject=self.subject,
            degree=self.degree,
            academic_year=self.academic_year,
            year="1r",
            term="1r Trimestre",
            group="GRUP 1"
        )
        self.degreesubject.save()

    def test_subject_duplicate_creation(self):
        duplicate_subject = Subject(
            faculty=self.faculty,
            name="Àlgebra"
        )
        self.assertRaises(IntegrityError, duplicate_subject.save)

    def test_class_duplicate_creation(self):
        duplicate_lesson = Lesson(
            subject=self.subject,
            group="GRUP 1",
            subgroup="S101",
            kind="TEORIA",
            room="52.349",
            date_start=datetime.datetime(2013, 4, 4, 10, 30, 00),
            date_end=datetime.datetime(2013, 4, 4, 12, 30, 00),
            academic_year=self.academic_year,
            raw_entry="Some similar stuff"
        )
        self.assertRaises(IntegrityError, duplicate_lesson.save)

    def test_degreesubject_duplicate_creation(self):
        duplicate_degreesubject = DegreeSubject(
            subject=self.subject,
            degree=self.degree,
            academic_year=self.academic_year,
            year="1r",
            term="1r Trimestre",
            group="GRUP 1"
        )
        self.assertRaises(IntegrityError, duplicate_degreesubject.save)


class CalendarCreationTests(TestCase):
    def test_calendar_creation_of_lessons(self):
        """
        """
        algebra_lessons = Lesson.objects.filter(
            subject__name__contains="Àlgebra",
            group='GRUP 1'
        )
        cal = Calendar()
        cal.add('prodid', '-//My calendar product//mxm.dk//')
        cal.add('version', '2.0')
        for entry in algebra_lessons:
            event = Event()
            event.add('summary', entry.subject.name + ' ' + entry.kind)
            event.add('dtstart', entry.date_start)
            event.add('dtend', entry.date_end)
            cal.add_component(event)
        f = open('test.ics', 'wb')
        f.write(cal.to_ical())
        f.close()
        self.assertEqual(1 + 1, 2)
