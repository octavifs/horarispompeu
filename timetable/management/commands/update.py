# encoding: utf-8
from django.core.management.base import NoArgsCommand
from django.conf import settings

from timetable import scraper
from timetable.models import DegreeSubject


class Command(NoArgsCommand):
    help = ("Update DB. Update lessons. Only selects "
            "calendars from current academic year and term, if defined")

    def handle_noargs(self, **options):
        if not settings.ACADEMIC_YEAR and not settings.TERM:
            raise ValueError("ACADEMIC_YEAR and TERM undefined in settings.")
        # Get all DegreeSubjects which have an active calendar AND are currently
        # active due to academic year and term
        degree_subjects = DegreeSubject.objects.exclude(calendar=None).filter(
            academic_year=settings.ACADEMIC_YEAR,
            term_key=settings.TERM
        ).distinct()
        self.stdout.write("Updating lessons. This will take a while...\n")
        scraper.populate_lessons(degree_subjects)
        self.stdout.write("DONE!\n")

