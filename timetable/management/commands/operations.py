# encoding: utf-8


def insert_lessons(lessons, group, academic_year):
    """
    Insert an iterable of _parser.Lesson to the DB as models.Lesson objects.
    The group and academic_year is necessary to complete the DB model.
    All lessons will be inserted as if they formed part of the same group and
    academic year.
    Returns True if any of the inserts hits the DB. False otherwise.
    """
    raise NotImplementedError()


def delete_lessons(lessons, group, academic_year):
    """
    Delete the related models.Lesson from an iterable of _parser.Lesson.
    Group and academic year are applied to all lessons from the iterable fine
    grain the select query.
    Returns True if any of the inserts hits the DB. False otherwise.
    """
    raise NotImplementedError()


def insert_subjectaliases(lessons):
    """
    Insert SubjectAlias linked to lesson.subject, if none is found in the DB.
    Returns True if any of the inserts hits the DB. False otherwise.
    """
    raise NotImplementedError()


def insert_degreesubjects(lessons, group, academic_year, degree, year, term):
    """
    Inserts lesson.subject to the DB as a new models.DegreeSubject object.
    Returns True if any of the inserts hits the DB. False otherwise.
    Raises exception if lesson.subject is not linked to any Subject in the DB
    (through a SubjectAlias object).
    """
    raise NotImplementedError()


def update_calendars(subjects=None):
    """
    Updates any calendar file whose DegreeSubjects match one of the Subject
    objects in the iterable. If subjects is None, update all calendars.
    Returns True if any calendar is updated. False otherwise.
    """
    raise NotImplementedError()
