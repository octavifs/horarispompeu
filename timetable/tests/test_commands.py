# encoding: utf-8

from django.test import TestCase


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
    pass
