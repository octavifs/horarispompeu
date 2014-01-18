# encoding: utf-8

from subprocess import Popen, PIPE
from datetime import datetime
from shutil import copyfile, copytree
import time

from django.core.management.base import NoArgsCommand
from django.core.mail import send_mail
from django.conf import settings


class Command(NoArgsCommand):
    help = (
        "Parse all subjects, lessons and update calendars. Utility script that "
        "basically calls all 3 previous commands and sends a mail with the "
        "output to the admins. And that's about it. This script should be put "
        "in a crontab, and run every 24h (at least)."
    )

    def handle_noargs(self, **options):
        start = time.time()
        message = "Starting update...\n"
        # First backup the DB & the html sources for the timetables
        copyfile('./resources/horaris.sqlite', './resources/backups/horaris.sqlite.{}'.format(datetime.now()))
        copytree('./resources/timetable', './resources/backups/timetable {}'.format(datetime.now()))
        # Parse subjects in search for new aliases
        subject_parser = Popen(["./manage.py", "subjectparser"], stdout=PIPE, stderr=PIPE)
        output, error = subject_parser.communicate()
        if output:
            message += output
        if error:
            message += error
        if subject_parser.returncode:  # If return code != 0, something wrong
            end = time.time()
            message += "Time employed: {} seconds\n".format(end - start)
            send_mail(
                "[HP] [UPDATE] [KO] {}".format(datetime.now()),
                message,
                "horarispompeu@gmail.com",
                [admin[1] for admin in settings.ADMINS],
                True
            )
            self.stderr.write("DONE. subjectparser KO")
            return
        lesson_parser = Popen(["./manage.py", "lessonparser"], stdout=PIPE, stderr=PIPE)
        output, error = lesson_parser.communicate()
        if output:
            message += output
        if error:
            message += error
        if lesson_parser.returncode:  # If return code != 0, something wrong
            end = time.time()
            message += "Time employed: {} seconds\n".format(end - start)
            send_mail(
                "[HP] [UPDATE] [KO] {}".format(datetime.now()),
                message,
                "horarispompeu@gmail.com",
                [admin[1] for admin in settings.ADMINS],
                True
            )
            self.stderr.write("DONE. lessonparser KO")
            return
        calendar_updater = Popen(["./manage.py", "calendarupdater"], stdout=PIPE, stderr=PIPE)
        output, error = calendar_updater.communicate()
        if output:
            message += output
        if error:
            message += error
        if calendar_updater.returncode:  # If return code != 0, something wrong
            end = time.time()
            message += "Time employed: {} seconds\n".format(end - start)
            send_mail(
                "[HP] [UPDATE] [KO] {}".format(datetime.now()),
                message,
                "horarispompeu@gmail.com",
                [admin[1] for admin in settings.ADMINS],
                True
            )
            self.stderr.write("DONE. calendarupdater KO")
            return
        # If everything has gone OK
        end = time.time()
        message += "Time employed: {} seconds\n".format(end - start)
        send_mail(
            "[HP] [UPDATE] [OK] {}".format(datetime.now()),
            message,
            "horarispompeu@gmail.com",
            [admin[1] for admin in settings.ADMINS],
            True
        )
        self.stdout.write("DONE. ALL OK")
