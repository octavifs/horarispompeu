# encoding: utf-8
from django.core.management.base import NoArgsCommand

from django.conf import settings
from timetable import scraper
from timetable.models import DegreeSubject


class Command(NoArgsCommand):
    help = "Populate DB. Slow. Run this on setup"

    def handle_noargs(self, **options):
        self.stdout.write("Populating Faculties, Degrees and Subjects. "
                          "This will take a while...\n")
        scraper.populate_db()
        self.stdout.write("DONE!\n")
        self.stdout.write("Populating Lessons. This will take even longer.\n")
        scraper.populate_lessons(DegreeSubject.objects.all())
        self.stdout.write("DONE!\n")
