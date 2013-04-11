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

    def test_ics_creation_from_lessons(self):
        lessons = Lesson.objects.filter(subject=self.subject, group='GRUP 1')
        calendar = timetable.calendar.generate(lessons)
        ics_string = b'BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//Calendari HorarisPompeu.com//mxm.dk//\r\nX-WR-CALNAME:horarispompeu.com\r\nBEGIN:VEVENT\r\nSUMMARY:TEORIA  \xc3\x80lgebra\r\nDTSTART;VALUE=DATE-TIME:20130404T083000Z\r\nDTEND;VALUE=DATE-TIME:20130404T103000Z\r\nLOCATION:52.349\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n'
        self.assertEqual(calendar, ics_string)

    def test_lesson_create_lessoninsert_create(self):
        lesson_insert = LessonInsert.objects.filter(lesson=self.lesson)
        self.assertEqual(len(lesson_insert), 1)

    def test_lesson_delete_lessoninsert_delete(self):
        self.lesson.delete()
        lesson_insert = LessonInsert.objects.filter(lesson=self.lesson)
        self.assertEqual(len(lesson_insert), 0)

    def test_lesson_delete_lessondelete_create(self):
        self.lesson.delete()
        lesson_delete = LessonDelete.objects.all()
        self.assertEqual(len(lesson_delete), 1)

    def test_lesson_delete_lessonarchive_create(self):
        self.lesson.delete()
        lesson_archive = LessonArchive.objects.all()
        self.assertEqual(len(lesson_archive), 1)

    def test_lessonarchive_delete(self):
        self.lesson.delete()
        lesson_archive = LessonArchive.objects.all()[0]
        lesson_archive.delete()
        self.assertEqual(lesson_archive.id, None)

    def test_lessonarchive_delete_lesson_not_recreate(self):
        self.lesson.delete()
        lesson_archive = LessonArchive.objects.all()[0]
        lesson_archive.delete()
        self.assertEqual(self.lesson.id, None)

    def test_lessonarchive_delete_lessondelete_delete(self):
        self.lesson.delete()
        lesson_archive = LessonArchive.objects.all()[0]
        lesson_archive.delete()
        lesson_deletes = LessonDelete.objects.all()
        self.assertEqual(len(lesson_deletes), 0)

    def test_lessondelete_delete_lessonarchive_delete(self):
        self.lesson.delete()
        lesson_delete = LessonDelete.objects.all()[0]
        lesson_delete.delete()
        lesson_archives = LessonArchive.objects.all()
        self.assertEqual(len(lesson_archives), 0)


class CalendarCreationTests(TestCase):
        pass


class CalendarUpdateTests(TestCase):
    """
    Tests to ensure that the functionality to detect added and removed classes
    is working. Tests that the hash() function returns different values in
    different strings (to detect changes in the html) and that the Lesson class
    from the _parser module has the necessary properties to operate as a set, so
    we can perform differences.
    """
    def test_equality_same_timetable_html(self):
        """Test if 2 calendars are equal"""
        with open('resources/calendar_html/horari1_old.html') as f:
            timetable_html = f.read()
        self.assertEqual(hash(timetable_html), hash(timetable_html))

    def test_inequality_different_timetable_html(self):
        """Test if 2 calendars are different"""
        with open('resources/calendar_html/horari1_old.html') as f:
            timetable_html_old = f.read()
        with open('resources/calendar_html/horari1_new.html') as f:
            timetable_html_new = f.read()
        self.assertNotEqual(hash(timetable_html_old), hash(timetable_html_new))

    def test_deleted_lessons(self):
        """Test difference operation with a set of Lessons. This is equivalent
        to a LEFT OUTER JOIN. That is, we only keep the distinct entries on the
        leftmost set. We will use this to get the deleted classes in an update.
        """
        lessonA = parser.Lesson()
        lessonA.subject = "A"
        lessonB = parser.Lesson()
        lessonB.subject = "B"
        lessonC = parser.Lesson()
        lessonC.subject = "C"
        lessonD = parser.Lesson()
        lessonD.subject = "D"
        lessons_old = set([lessonA, lessonB, lessonC])
        lessons_new = set([lessonB, lessonC, lessonD])
        # Lessons deleted should only hold lessonA
        lessons_deleted = set(lessons_old) - set(lessons_new)
        self.assertEqual(lessons_deleted.pop(), lessonA)

    def test_added_lessons(self):
        """Test difference operation with a set of Lessons. This is equivalent
        to a RIGHT OUTER JOIN. That is, we only keep the distinct entries on the
        rightmost set. We will use this to get the added classes in an update.
        """
        lessonA = parser.Lesson()
        lessonA.subject = "A"
        lessonB = parser.Lesson()
        lessonB.subject = "B"
        lessonC = parser.Lesson()
        lessonC.subject = "C"
        lessonD = parser.Lesson()
        lessonD.subject = "D"
        lessons_old = set([lessonA, lessonB, lessonC])
        lessons_new = set([lessonB, lessonC, lessonD])
        lessons_added = set(lessons_new) - set(lessons_old)
        # Lessons added should only hold lessonD
        self.assertEqual(lessons_added.pop(), lessonD)

    def test_parser_lesson_equality(self):
        lesson1 = parser.Lesson()
        lesson1.subject = "Class 1. Bla, bla, bla"
        lesson2 = parser.Lesson()
        lesson2.subject = lesson1.subject
        self.assertEqual(lesson1, lesson2)

    def test_parser_lesson_inequality(self):
        lesson1 = parser.Lesson()
        lesson1.subject = "Class 1. Bla, bla, bla"
        lesson2 = parser.Lesson()
        lesson2.subject = "Something else from Class 1"
        self.assertNotEqual(lesson1, lesson2)
