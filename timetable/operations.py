# encoding: utf-8
from django.core.files.base import ContentFile
from timetable.models import SubjectAlias, DegreeSubject, Lesson, Calendar
from timetable import calendar as ical


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
            entry=lesson.data if lesson.data else "",
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
    # We start with no matches
    matches = Lesson.objects.none()
    for lesson in lessons:
        try:
            alias = SubjectAlias.objects.get(name=lesson.subject)
        except SubjectAlias.DoesNotExist:
            alias = None
        # Start with an unfiltered QuerySet, and progressively add them
        match = Lesson.objects.all()
        # Add as many filters as possible, given that the field is available
        # The style is a bit cumbersome, but if we didn't perform the check
        # and add filters such as subject=None, the QuerySet would try to match
        # entries with Null fields, instead of ignoring the filtering on that
        # specific field.
        if alias and alias.subject:
            match = match.filter(subject=alias.subject)
        if group:
            match = match.filter(group=group)
        if lesson.date_start:
            # We are only interested in filtering by date, not hour. This is
            # because the parser may not parse the time correctly.
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
        if lesson.data:
            match = match.filter(entry=lesson.data)
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
    updated_calendars = False
    if not subjects:
        calendars = Calendar.objects.all()
    else:
        calendars = Calendar.objects.none()
        for subject in subjects:
            calendars = calendars | Calendar.objects.filter(
                degree_subjects__subject=subject)
        calendars = calendars.distinct()
    for calendar in calendars:
        lessons = Lesson.objects.none()
        for degreesubject in calendar.degree_subjects.all():
            lessons = lessons | degreesubject.lessons()
        lessons = lessons.distinct()
        calendar_string = ical.generate(lessons)
        try:
            calendar.file.delete()
        except OSError:
            # File already deleted. No need to do anything.
            pass
        calendar.file.save(calendar.name + '.ics', ContentFile(calendar_string))
        updated_calendars = True
    return updated_calendars
