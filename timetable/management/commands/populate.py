# encoding: utf-8

from django.core.management.base import NoArgsCommand

from django.conf import settings
from timetable import scraper
from timetable.models import DegreeSubject


class Command(NoArgsCommand):
    help = ("Update DB. Update lessons and rewrite calendars. Only selects "
            "calendars from current academic year and term, if defined")

    def handle_noargs(self, **options):
        if not settings.ACADEMIC_YEAR or not settings.TERM:
            raise ValueError("ACADEMIC_YEAR or TERM undefined in settings.")
        self.stdout.write("Populating Faculties, Degrees and Subjects. "
                          "This will take a while...\n")
        scraper.populate_db()
        self.stdout.write("DONE!\n")
        self.stdout.write("Populating Lessons. This will take even longer.\n")
        scraper.populate_db(DegreeSubject.objects.all())
        self.stdout.write("DONE!\n")
