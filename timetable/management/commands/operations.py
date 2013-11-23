# encoding: utf-8
from django.db.models.query import QuerySet
from timetable.models import SubjectAlias, DegreeSubject, Lesson


def insert_lessons(lessons, group, academic_year):
    """
    Insert an iterable of _parser.Lesson to the DB as models.Lesson objects.
    The group and academic_year is necessary to complete the DB model.
    All lessons will be inserted as if they formed part of the same group and
    academic year.
    Returns True if any of the inserts hits the DB. False otherwise.
    """
    new_lessons = False
    for lesson in lessons:
        alias, created = SubjectAlias.objects.get_or_create(name=lesson.subject)
        l, created = Lesson.objects.get_or_create(
            subject=alias.subject,
            group=group,
            subgroup=lesson.group if lesson.group else "",
            kind=lesson.kind if lesson.kind else "",
            room=lesson.room if lesson.room else "",
            date_start=lesson.date_start,
            date_end=lesson.date_end,
            academic_year=academic_year,
            raw_entry=lesson.raw_data if lesson.raw_data else "",
        )
        new_lessons = new_lessons or created
    return new_lessons


def delete_lessons(lessons, group, academic_year):
    """
    Delete the related models.Lesson from an iterable of _parser.Lesson.
    Group and academic year are applied to all lessons from the iterable fine
    grain the select query.
    Returns True if any of the deletions hits the DB. False otherwise.
    """
    deleted_lessons = False
    matches = Lesson.objects.none()
    for lesson in lessons:
        try:
            alias = SubjectAlias.objects.get(name=lesson.subject)
        except SubjectAlias.DoesNotExist:
            alias = None
        match = Lesson.objects.all()
        # Add as many filters as possible, given that the field is available
        if alias and alias.subject:
            match = match.filter(subject=alias.subject)
        if group:
            match = match.filter(group=group)
        if lesson.group:
            match = match.filter(subgroup=lesson.group)
        if lesson.kind:
            match = match.filter(kind=lesson.kind)
        if lesson.room:
            match = match.filter(room=lesson.room)
        if lesson.date_start:
            match = match.filter(
                date_start__day=lesson.date_start.day,
                date_start__month=lesson.date_start.month,
                date_start__year=lesson.date_start.year,
            )
        if lesson.date_end:
            match = match.filter(
                date_end__day=lesson.date_end.day,
                date_end__month=lesson.date_end.month,
                date_end__year=lesson.date_end.year,
            )
        if academic_year:
            match = match.filter(academic_year=academic_year)
        if lesson.raw_data:
            match = match.filter(raw_entry=lesson.raw_data)
        # Add match filter to the macrofilter
        matches = matches | match
    # We don't want repeated entries
    matches = matches.distinct()
    for m in matches:
        m.delete()
    deleted_lessons = matches.exists()
    return deleted_lessons


def insert_subjectaliases(lessons):
    """
    Insert SubjectAlias linked to lesson.subject, if none is found in the DB.
    Returns True if any of the inserts hits the DB. False otherwise.
    """
    new_alias = False
    for lesson in lessons:
        alias, created = SubjectAlias.objects.get_or_create(name=lesson.subject)
        new_alias = new_alias or created
    return new_alias


def insert_degreesubjects(lessons, group, academic_year, degree, year, term):
    """
    Inserts lesson.subject to the DB as a new models.DegreeSubject object.
    Returns True if any of the inserts hits the DB. False otherwise.
    Raises exception if lesson.subject is not linked to any Subject in the DB
    (through a SubjectAlias object).
    """
    new_degreesubject = False
    for lesson in lessons:
        # This will raise a SubjectAlias.DoesNotExist if trying to insert a
        # subject without its corresponding alias object.
        alias = SubjectAlias.objects.get(name=lesson.subject)
        # Get the object if exists or create it if not
        degreesubject, created = DegreeSubject.objects.get_or_create(
            subject=alias.subject,
            degree=degree,
            academic_year=academic_year,
            year=year,
            term=term,
            group=group,
        )
        new_degreesubject = new_degreesubject or created
    return new_degreesubject


def update_calendars(subjects=None):
    """
    Updates any calendar file whose DegreeSubjects match one of the Subject
    objects in the iterable. If subjects is None, update all calendars.
    Returns True if any calendar is updated. False otherwise.
    """
    raise NotImplementedError()
