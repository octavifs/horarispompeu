# encoding: utf-8
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from __future__ import unicode_literals
from django.test import TestCase
from django.db import IntegrityError
from django.core.files.base import ContentFile
import codecs
from timetable.models import *
import datetime
import timetable.calendar
import timetable.updater
import timetable.management.commands._parser as parser


class DatabaseTests(TestCase):
    """
    Tests that insertion of duplicates in the DB model raises IntegrityError
    exception.
    Also tests that check the way ManyToMany and FileField work (from Calendar
    model)
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
        self.subject2 = Subject(
            faculty=self.faculty,
            name="Càlcul"
        )
        self.subject2.save()
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
        duplicate_lesson = self.lesson
        duplicate_lesson.pk = None
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

    def test_calendar_creation(self):
        calendar = Calendar(name="hola")
        calendar2 = Calendar(name="hola")
        calendar2.save()
        calendar.file.save("hola", ContentFile("HOLAHOLA"))
        calendar.save()
        self.assertEqual(calendar.file.url, "")

    def test_ics_creation_from_lessons(self):
        lessons = Lesson.objects.filter(subject=self.subject, group='GRUP 1')
        calendar = timetable.calendar.generate(lessons)
        ics_string = b'BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//Calendari HorarisPompeu.com//mxm.dk//\r\nX-WR-CALNAME:horarispompeu.com\r\nBEGIN:VEVENT\r\nSUMMARY:TEORIA  \xc3\x80lgebra\r\nDTSTART;VALUE=DATE-TIME:20130404T083000Z\r\nDTEND;VALUE=DATE-TIME:20130404T103000Z\r\nLOCATION:52.349\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n'
        self.assertEqual(calendar, ics_string)


class CalendarCreationTests(TestCase):
        pass


class CalendarUpdateTests(TestCase):
    def test_equality_same_timetable_html(self):
        with open('resources/calendar_html/horari1_old.html') as f:
            timetable_html = f.read()
        isEqual = timetable.updater.is_html_equal(timetable_html, timetable_html)
        self.assertTrue(isEqual)

    def test_inequality_different_timetable_html(self):
        with open('resources/calendar_html/horari1_old.html') as f:
            timetable_html_old = f.read()
        with open('resources/calendar_html/horari1_new.html') as f:
            timetable_html_new = f.read()
        isEqual = timetable.updater.is_html_equal(timetable_html_old, timetable_html_new)
        self.assertFalse(isEqual)

    def test_substracted_lessons(self):
        with codecs.open('resources/calendar_html/horari1_old.html') as f:
            timetable_html_old = f.read()
        with codecs.open('resources/calendar_html/horari1_new.html') as f:
            timetable_html_new = f.read()
        lessons = timetable.updater.substracted_lessons(timetable_html_old, timetable_html_new)
        self.assertEqual(len(lessons), 1)

    def test_added_lessons(self):
        with codecs.open('resources/calendar_html/horari1_old.html') as f:
            timetable_html_old = f.read()
        with codecs.open('resources/calendar_html/horari1_new.html') as f:
            timetable_html_new = f.read()
        lessons = timetable.updater.added_lessons(timetable_html_old, timetable_html_new)
        self.assertEqual(len(lessons), 1)

    def test_parser_lesson_equality(self):
        lesson1 = parser.Lesson()
        lesson1.raw_data = "Class 1. Bla, bla, bla"
        lesson2 = parser.Lesson()
        lesson2.raw_data = lesson1.raw_data
        self.assertEqual(lesson1, lesson2)

    def test_parser_lesson_inequality(self):
        lesson1 = parser.Lesson()
        lesson1.raw_data = "Class 1. Bla, bla, bla"
        lesson2 = parser.Lesson()
        lesson2.raw_data = "Something else from Class 1"
        self.assertNotEqual(lesson1, lesson2)

