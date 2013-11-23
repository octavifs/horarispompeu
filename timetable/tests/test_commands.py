# encoding: utf-8
from __future__ import unicode_literals
from django.test import TestCase
from datetime import datetime
from timetable.models import Faculty, Subject, SubjectAlias, AcademicYear, Degree, DegreeSubject, Lesson
from timetable.management.commands import _parser as parser
from timetable.management.commands import operations


class CommandTests(TestCase):
    """
    Test suite for the timetable.management.commands.operations module.
    It tests that the addition and deletion of lessons (obtained form the parser
    module) is correctly managed by the database.
    It basically deals with:
        - Lesson insertions
        - Lesson deletions
        - SubjectAlias insertions
        - DegreeSubject insertions
        - Calendar updates
    """
    def setUp(self):
        self.lessons = [
            parser.Lesson(
                subject="Polítiques Públiques de TIC",
                kind="PRÀCTIQUES",
                room="52.119",
                date_start=datetime(2013, 12, 2, 8, 30),
                date_end=datetime(2013, 12, 2, 10, 30),
            ),
            parser.Lesson(
                subject="Aplicacions Intel·ligents per a la Web",
                kind="PRÀCTIQUES",
                group="P101",
                room="54.004",
                date_start=datetime(2013, 12, 3, 8, 30),
                date_end=datetime(2013, 12, 3, 10, 30),
            ),
            parser.Lesson(
                subject="Robòtica",
                kind="PRÀCTIQUES",
                group="P101",
                room="54.003",
                date_start=datetime(2013, 12, 3, 8, 30),
                date_end=datetime(2013, 12, 3, 10, 30),
            ),
            parser.Lesson(
                subject="Aplicacions Intel·ligents per a la Web",
                kind="PRÀCTIQUES",
                group="P102",
                room="54.004",
                date_start=datetime(2013, 12, 4, 12, 30),
                date_end=datetime(2013, 12, 4, 14, 30),
            ),
            parser.Lesson(
                subject="Projectes Basats en Software Lliure",
                kind="PRÀCTIQUES",
                group="P101",
                room="54.005",
                date_start=datetime(2013, 12, 3, 14, 30),
                date_end=datetime(2013, 12, 3, 16, 30),
            ),
            parser.Lesson(
                subject="Projectes Basats en Software Lliure",
                kind="PRÀCTIQUES",
                group="P101",
                room="54.003",
                date_start=datetime(2013, 12, 4, 18, 30),
                date_end=datetime(2013, 12, 4, 20, 30),
            ),
        ]
        self.esup = Faculty(name="ESUP")
        self.esup.save()
        self.subjects = [
            Subject(faculty=self.esup, name="Polítiques Públiques de TIC"),
            Subject(faculty=self.esup, name="Aplicacions Intel·ligents per a la Web"),
            Subject(faculty=self.esup, name="Projectes Basats en Software Lliure"),
            Subject(faculty=self.esup, name="Robòtica"),
        ]
        for s in self.subjects:
            s.save()
        self.subjectaliases = [
            SubjectAlias(subject=self.subjects[0], name="Polítiques Públiques de TIC"),
            SubjectAlias(subject=self.subjects[1], name="Aplicacions Intel·ligents per a la Web"),
            SubjectAlias(subject=self.subjects[2], name="Projectes Basats en Software Lliure"),
            SubjectAlias(subject=self.subjects[3], name="Robòtica"),
        ]
        for s in self.subjectaliases:
            s.save()
        self.academic_year = AcademicYear(year="2013/14")
        self.academic_year.save()
        self.degree = Degree(faculty=self.esup, name="Informàtica")
        self.degree.save()

    def test_insert_subjectaliases(self):
        # Inserting self.lessons should return false, since all the data is
        # already in the DB (see setUp method).
        self.assertFalse(operations.insert_subjectaliases(self.lessons))

        # Insert a new lesson with a variation in the name, so an alias must be
        # added.
        lessons = [
            parser.Lesson(
                subject="Robotica",
                kind="PRÀCTIQUES",
                group="P101",
                room="54.003",
                date_start=datetime(2013, 12, 3, 8, 30),
                date_end=datetime(2013, 12, 3, 10, 30),
            ),
        ]
        # When calling the insert function, it should return True now
        self.assertTrue(operations.insert_subjectaliases(lessons))
        # Check that the object exists in the DB
        self.assertTrue(SubjectAlias.objects.get(name="Robotica"))

    def test_insert_degreesubjects(self):
        lessons = [
            parser.Lesson(
                subject="Robòtica",
                kind="PRÀCTIQUES",
                group="P101",
                room="54.003",
                date_start=datetime(2013, 12, 3, 8, 30),
                date_end=datetime(2013, 12, 3, 10, 30),
            ),
        ]
        self.assertTrue(operations.insert_degreesubjects(
            lessons,
            "GRUP 1",
            self.academic_year,
            self.degree,
            "1r",
            "1r Trimestre"
        ))
        # Check that the DegreeSubject has been created
        subject = Subject.objects.get(name="Robòtica")
        self.assertTrue(DegreeSubject.objects.get(subject=subject))

        # Repeating the insert should return False now
        self.assertFalse(operations.insert_degreesubjects(
            lessons,
            "GRUP 1",
            self.academic_year,
            self.degree,
            "1r",
            "1r Trimestre"
        ))

        # Try to insert a DegreeSubject for a lesson not aliased in the DB
        lessons = [
            parser.Lesson(
                subject="No Alias Available",
                kind="PRÀCTIQUES",
                group="P101",
                room="54.003",
                date_start=datetime(2013, 12, 3, 8, 30),
                date_end=datetime(2013, 12, 3, 10, 30),
            ),
        ]
        self.assertRaises(
            SubjectAlias.DoesNotExist,
            operations.insert_degreesubjects,
            lessons,
            "GRUP 1",
            self.academic_year,
            self.degree,
            "1r",
            "1r Trimestre"
        )

    def test_insert_lessons(self):
        # Insert lessons to the DB
        self.assertTrue(
            operations.insert_lessons(self.lessons, "GRUP 1", self.academic_year)
        )
        # Check that there are len(self.lessons) to the DB
        self.assertEqual(len(self.lessons), len(Lesson.objects.all()))

        # Try to insert same lessons again
        self.assertFalse(
            operations.insert_lessons(self.lessons, "GRUP 1", self.academic_year)
        )

        # Insert a partial lesson
        lessons = [
            parser.Lesson(
                subject="No Alias Available",
                kind=None,
                group=None,
                room=None,
                date_start=datetime(2013, 12, 3, 8, 30),
                date_end=datetime(2013, 12, 3, 10, 30),
            ),
        ]
        self.assertTrue(
            operations.insert_lessons(lessons, "GRUP 1", self.academic_year)
        )

    def test_delete_lessons(self):
        # Insert lessons to the DB
        self.assertTrue(
            operations.insert_lessons(self.lessons, "GRUP 1", self.academic_year)
        )
        # Delete lessons from the DB
        self.assertTrue(
            operations.delete_lessons(self.lessons, "GRUP 1", self.academic_year)
        )
        # Check that there are no Lessons in the DB
        self.assertFalse(Lesson.objects.all().exists())
        # Delete a lesson with partial information form the DB. In this case,
        # we will have manually filled various entries in the DB, and the lesson
        # will match and delete those entries:
        l = Lesson(
            subject=Subject.objects.get(name="Polítiques Públiques de TIC"),
            group="GRUP 1",
            subgroup="S101",
            kind="SEMINARI",
            room="52.105",
            date_start=datetime(2013, 11, 11, 10, 30),
            date_end=datetime(2013, 11, 11, 11, 30),
            raw_entry="Polítiques Públiques de TIC\n Seminari\n S101",
            academic_year=self.academic_year
        )
        l.save()
        subject = Subject.objects.get(name="Robòtica")
        l = Lesson(
            subject=subject,
            group="GRUP 1",
            subgroup="S101",
            kind="SEMINARI",
            room="52.105",
            date_start=datetime(2013, 11, 11, 10, 30),
            date_end=datetime(2013, 11, 11, 11, 30),
            raw_entry="Robòtica\n Seminari\n S101",
            academic_year=self.academic_year
        )
        l.save()
        l = Lesson(
            subject=subject,
            group="GRUP 1",
            subgroup="S102",
            kind="SEMINARI",
            room="52.105",
            date_start=datetime(2013, 11, 11, 11, 30),
            date_end=datetime(2013, 11, 11, 12, 30),
            raw_entry="Robòtica\n Seminari\n S101",
            academic_year=self.academic_year
        )
        l.save()
        # Suppose the parser broke and we only have the raw data and the
        # approximate date of the class
        lessons = [
            parser.Lesson(
                date_start=datetime(2013, 11, 11, 10, 30),
                date_end=datetime(2013, 11, 11, 12, 30),
                raw_data="Robòtica\n Seminari\n S101"
            ),
        ]
        self.assertTrue(
            operations.delete_lessons(lessons, "GRUP 1", self.academic_year)
        )
        self.assertFalse(Lesson.objects.filter(subject=subject).exists())
