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

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test timetable".

Run them from the folder where manage.py is stored. (or the last 4 tests will, probably, fail)
"""
#from __future__ import unicode_literals
from django.test import TestCase
from django.db import IntegrityError
from django.core.files.base import ContentFile
from timetable.models import *
import datetime
import timetable.calendar
import timetable.updater
import timetable.management.commands._parser as parser
import timetable.management.commands.lessonparser as lessonparser
import timetable.management.commands.initdb as initdb
import timetable.management.commands.subjectparser as subjectparser


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
        ics_string = 'BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//Calendari HorarisPompeu.com//mxm.dk//\r\nX-WR-CALNAME:horarispompeu.com\r\nBEGIN:VEVENT\r\nSUMMARY:TEORIA  \xc3\x80lgebra\r\nDTSTART;VALUE=DATE-TIME:20130404T103000\r\nDTEND;VALUE=DATE-TIME:20130404T123000\r\nLOCATION:52.349\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n'
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

    def test_degreesubjects_lessons(self):
        self.assertEquals(self.degreesubject.lessons()[0], self.lesson)
        self.assertEquals(len(self.degreesubject.lessons()), 1)


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
        with open('timetable/tests/calendar_html/horari1_old.html') as f:
            timetable_html = f.read()
        self.assertEqual(hash(timetable_html), hash(timetable_html))

    def test_inequality_different_timetable_html(self):
        """Test if 2 calendars are different"""
        with open('timetable/tests/calendar_html/horari1_old.html') as f:
            timetable_html_old = f.read()
        with open('timetable/tests/calendar_html/horari1_new.html') as f:
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

    def test_lesson_is_deleted_when_change(self):
        """Test that when a source calendar is changed, the old entries are deleted"""
        url = "http://theharpy.net/test_horaris_1213_GEI_C4_T1_G1.html"
        file_path = "timetable/tests/test_horaris_1213_GEI_C4_T1_G1.html"
        # Load the database
        initdb.Command().handle_noargs()
        subjectparser.Command().handle_noargs()
        # Parse old html lessons & put them into DB
        f = open(file_path)
        old_html = f.read()
        f.close()
        lessons = parser.parse(old_html)
        command = lessonparser.Command()
        command.insert(
            inserted_lessons=lessons,
            degree="Grau en Enginyeria en Informàtica",
            year="4t",
            term="1r Trimestre",
            group="GRUP 1",
        )
        # Check whether the lesson has been inserted or not (it will throw an exception if not)
        alias = SubjectAlias.objects.get(name="Càlcul i Mètodes Numèrics")
        Lesson.objects.get(
            subject=alias.subject,
            group="GRUP 1",
            subgroup="",
            kind="TEORIA",
            room="52.119",
            date_start=datetime.datetime(2012, 9, 25, 16, 30, 00),
            date_end=datetime.datetime(2012, 9, 25, 18, 30, 00),
        )
        # Update lessons with the "new" url
        command.update(
            degree="Grau en Enginyeria en Informàtica",
            year="4t",
            term="1r Trimestre",
            group="GRUP 1",
            url=url,
            file_path=file_path,
            overwrite=False
        )
        # Check that the lesson has been deleted
        self.assertRaises(
            Lesson.DoesNotExist,
            Lesson.objects.get,
            subject=alias.subject,
            group="GRUP 1",
            subgroup="",
            kind="TEORIA",
            room="52.119",
            date_start=datetime.datetime(2012, 9, 25, 16, 30, 00),
            date_end=datetime.datetime(2012, 9, 25, 18, 30, 00),
        )

    def test_lesson_is_inserted_when_change(self):
        """Test that when a source calendar is changed, the new entries are inserted"""
        url = "http://theharpy.net/test_horaris_1213_GEI_C4_T1_G1.html"
        file_path = "timetable/tests/test_horaris_1213_GEI_C4_T1_G1.html"
        # Load the database
        initdb.Command().handle_noargs()
        subjectparser.Command().handle_noargs()
        # Parse old html lessons & put them into DB
        f = open(file_path)
        old_html = f.read()
        f.close()
        lessons = parser.parse(old_html)
        command = lessonparser.Command()
        command.insert(
            inserted_lessons=lessons,
            degree="Grau en Enginyeria en Informàtica",
            year="4t",
            term="1r Trimestre",
            group="GRUP 1",
        )
        # Update lessons with the "new" url
        command.update(
            degree="Grau en Enginyeria en Informàtica",
            year="4t",
            term="1r Trimestre",
            group="GRUP 1",
            url=url,
            file_path=file_path,
            overwrite=False
        )
        alias = SubjectAlias.objects.get(name="Economia del Coneixement")
        lesson = Lesson.objects.get(
            subject=alias.subject,
            group="GRUP 1",
            subgroup="",
            kind="TEORIA",
            room="52.119",
            date_start=datetime.datetime(2012, 9, 25, 16, 30, 00),
            date_end=datetime.datetime(2012, 9, 25, 18, 30, 00),
        )
        self.assertNotEqual(lesson, None)

    def test_modified_degree_subjects_returned_when_change(self):
        url = "http://theharpy.net/test_horaris_1213_GEI_C4_T1_G1.html"
        file_path = "timetable/tests/test_horaris_1213_GEI_C4_T1_G1.html"
        # Load the database
        initdb.Command().handle_noargs()
        subjectparser.Command().handle_noargs()
        # Parse old html lessons & put them into DB
        f = open(file_path)
        old_html = f.read()
        f.close()
        lessons = parser.parse(old_html)
        command = lessonparser.Command()
        command.insert(
            inserted_lessons=lessons,
            degree="Grau en Enginyeria en Informàtica",
            year="4t",
            term="1r Trimestre",
            group="GRUP 1",
        )
        # Update lessons with the "new" url
        modified_degreesubjects = command.update(
            degree="Grau en Enginyeria en Informàtica",
            year="4t",
            term="1r Trimestre",
            group="GRUP 1",
            url=url,
            file_path=file_path,
            overwrite=False
        )
        self.assertEquals(len(modified_degreesubjects), 2)

    def test_updated_calendars_when_change(self):
        url = "http://theharpy.net/test_horaris_1213_GEI_C4_T1_G1.html"
        file_path = "timetable/tests/test_horaris_1213_GEI_C4_T1_G1.html"
        # Load the database
        initdb.Command().handle_noargs()
        subjectparser.Command().handle_noargs()
        # Parse old html lessons & put them into DB
        f = open(file_path)
        old_html = f.read()
        f.close()
        lessons = parser.parse(old_html)
        command = lessonparser.Command()
        command.insert(
            inserted_lessons=lessons,
            degree="Grau en Enginyeria en Informàtica",
            year="4t",
            term="1r Trimestre",
            group="GRUP 1",
        )
        lessons_db = Lesson.objects.all()
        degreesubjects = DegreeSubject.objects.all()
        old_calendar = Calendar(name="test_calendar")
        old_calendar.save()
        old_calendar.degree_subjects.add(*degreesubjects)
        old_calendar.file.save(old_calendar.name + '.ics',
                               ContentFile(timetable.calendar.generate(lessons_db)))
        old_calendar_ics = timetable.calendar.generate(lessons_db)
        # Update lessons with the "new" url
        modified_degreesubjects = command.update(
            degree="Grau en Enginyeria en Informàtica",
            year="4t",
            term="1r Trimestre",
            group="GRUP 1",
            url=url,
            file_path=file_path,
            overwrite=False
        )
        command.update_calendars(modified_degreesubjects)
        new_calendar = Calendar.objects.all()[0]
        new_calendar_ics = new_calendar.file.read()
        self.assertNotEqual(old_calendar_ics, new_calendar_ics)
