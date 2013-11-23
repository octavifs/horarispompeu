# encoding: utf-8

from django.core.management.base import NoArgsCommand

from timetable import operations


class Command(NoArgsCommand):
    help = "Update all calendar files"

    def handle_noargs(self, **options):
        self.stdout.write("Updating calendars, this may take a while...")
        operations.update_calendars()
        self.stdout.write("DONE!")
