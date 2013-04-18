# encoding: utf-8
from django.core.management.base import NoArgsCommand
from django.db.utils import IntegrityError
import requests
from django.db.models.query import QuerySet
import operator
from django.core.files.base import ContentFile
from django.db.models import Q
from timetable.models import *
from _esup_timetable_data import *
import _parser as parser
import timetable.calendar


class Command(NoArgsCommand):
    help = "Parse lessons and subjects from the ESUP degrees"

    def handle_noargs(self, **options):
        # Empty QuerySet that will hold all modified DegreeSubjects
        modified_degreesubjects = QuerySet(model=DegreeSubject)
        for degree, years in COMPULSORY_SUBJECTS_TIMETABLES.iteritems():
            for year, terms in years.iteritems():
                for term, groups in terms.iteritems():
                    for group, url, file_path in groups:
                        modified_degreesubjects = modified_degreesubjects | self.update(
                            degree,
                            year,
                            term,
                            group,
                            url,
                            file_path
                        )
        for degree in COMPULSORY_SUBJECTS_TIMETABLES:
            for term, groups in OPTIONAL_SUBJECTS_TIMETABLES.iteritems():
                for group, url, file_path in groups:
                    modified_degreesubjects = modified_degreesubjects | self.update(
                        degree,
                        "optatives",
                        term,
                        group,
                        url,
                        file_path
                    )
        self.update_calendars(modified_degreesubjects)

    def update(self, degree, year, term, group, url, file_path, overwrite=True):
        print ""
        print url
        # Get HTML from the ESUP website
        r = requests.get(url)
        r.encoding = 'ISO-8859-1'  # Force latin-1 encoding
        new_html = r.text
        # Get HTML from previous run
        try:
            f = open(file_path)
            old_html = f.read()
            f.close()
        except IOError:
            # If old html could not be opened. Alert about it but go on
            print "Could not open " + file_path
            old_html = ""
        # Check for differences. If equal, no need to process it.
        if hash(old_html) == hash(new_html):
            print "\tNo changes since last update..."
            return QuerySet(model=DegreeSubject)
        print "\tUpdating..."
        # Parse old html into a set of parser.Lessons
        old_lessons = set(parser.parse(old_html))
        # Parse new html into a set of parser.Lessons
        new_lessons = set(parser.parse(new_html))
        # Compute deleted & the inserted lessons.
        deleted_lessons = old_lessons - new_lessons  # set difference
        inserted_lessons = new_lessons - old_lessons  # set difference
        # Delete outdated lessons
        self.delete(deleted_lessons, degree, year, term, group)
        # Insert updated lessons
        self.insert(inserted_lessons, degree, year, term, group)
        # Update old HTML
        try:
            if overwrite:
                f = open(file_path, 'w')
                f.write(new_html)
                f.close()
        except IOError:
            # If old html could not be written. Alert about it but go on
            print "Could not write " + file_path
            print "HTML not updated"
        #
        # Create a list of modified DegreeSubjects
        #
        # First, collect changed lessons
        modified_lessons = deleted_lessons | inserted_lessons  # set union
        # select SubjectAlias that contain a subject that has changed
        q_list = (Q(name=lesson.subject) for lesson in modified_lessons)
        modified_subjectaliases = SubjectAlias.objects.filter(reduce(operator.or_, q_list))
        # select all Subjects referred by its SubjectAlias
        q_list = (Q(subject=alias.subject) for alias in modified_subjectaliases)
        modified_degreesubjects = DegreeSubject.objects.filter(reduce(operator.or_, q_list))
        return modified_degreesubjects

    def delete(self, deleted_lessons, degree, year, term, group):
        academic_year = AcademicYear.objects.get(year='2012-13')
        for entry in deleted_lessons:
            alias = entry.subject
            try:
                subject = SubjectAlias.objects.get(name=alias).subject
            except SubjectAlias.DoesNotExist, e:
                raise e
            try:
                lesson = Lesson.objects.get(
                    subject=subject,
                    group=group,
                    subgroup=entry.group,
                    kind=entry.kind,
                    room=entry.room,
                    date_start=entry.date_start,
                    date_end=entry.date_end,
                    academic_year=academic_year
                )
                lesson.delete()
            except Lesson.DoesNotExist:
                pass

    def insert(self, inserted_lessons, degree, year, term, group):
        faculty = Faculty.objects.get(name='ESUP')
        academic_year = AcademicYear.objects.get(year='2012-13')
        # create degreesubjects
        for entry in inserted_lessons:
            alias = entry.subject
            try:
                subject = SubjectAlias.objects.get(name=alias).subject
            except SubjectAlias.DoesNotExist, e:
                raise e
            degree_obj = Degree.objects.get(name=degree, faculty=faculty)
            degreesubject = DegreeSubject(
                subject=subject,
                degree=degree_obj,
                academic_year=academic_year,
                year=year,
                term=term,
                group=group
            )
            try:
                degreesubject.save()
            except IntegrityError:
                # This will trigger when trying to add a duplicate entry
                pass
        # create lessons
        for entry in inserted_lessons:
            alias = entry.subject
            subject = SubjectAlias.objects.get(name=alias).subject
            lesson = Lesson(
                subject=subject,
                group=group,
                subgroup=entry.group,
                kind=entry.kind,
                room=entry.room,
                date_start=entry.date_start,
                date_end=entry.date_end,
                academic_year=academic_year,
                raw_entry=entry.raw_data,
            )
            try:
                lesson.save()
            except IntegrityError:
                # This will trigger when trying to add a duplicate entry
                pass

    def update_calendars(self, degree_subjects):
        calendars = Calendar.objects.filter(degree_subjects=degree_subjects)
        for calendar in calendars:
            lessons = QuerySet(model=Lesson)
            for degreesubject in calendar.degree_subjects.all():
                lessons = lessons | degreesubject.lessons()
            lessons = lessons.distinct()
            #lessons = reduce(operator.or_, calendar.degree_subjects.lessons)
            calendar_string = timetable.calendar.generate(lessons)
            try:
                calendar.file.delete()
            except OSError:
                # File already deleted. No need to do anything.
                pass
            calendar.file.save(calendar.name + '.ics',
                               ContentFile(calendar_string))
