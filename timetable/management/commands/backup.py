# encoding: utf-8

from subprocess import Popen, PIPE
from datetime import datetime
from shutil import copyfile
import time
import traceback
from os import path

from boto.s3.connection import S3Connection
from boto.s3.key import Key

from django.core.management.base import NoArgsCommand
from django.core.mail import send_mail
from django.conf import settings


class Command(NoArgsCommand):
    help = (
        "Parse all lessons and update calendars. Utility script that "
        "basically calls all 3 previous commands and sends a mail with the "
        "output to the admins. And that's about it. This script should be put "
        "in a crontab, and run every 24h (at least)."
    )

    def handle_noargs(self, **options):
        start = time.time()
        now = datetime.now()
        message = "Starting update...\n"
        # First backup the DB & the html sources for the timetables
        copyfile(path.join(settings.BASE_DIR, 'resources/horaris.sqlite'),
                 path.join(settings.BASE_DIR,
                           'resources/backups/horaris.sqlite.{}'.format(now)))
        # Also backup the DB and private config to S3 (if settings say so)
        if settings.S3_BACKUP:
            try:
                conn = S3Connection(settings.AWS_ACCESS_KEY,
                                    settings.AWS_SECRET_KEY)
                bucket = conn.get_bucket(settings.S3_BUCKET)
                database = Key(bucket)
                database.key = '/{}/horaris.sqlite'.format(now)
                database.set_contents_from_filename(
                    path.join(settings.BASE_DIR, 'resources/horaris.sqlite'))
                message += 'Uploaded DB to S3\n'
                private_settings = Key(bucket)
                private_settings.key = '/{}/settings_private.py'.format(now)
                private_settings.set_contents_from_filename(
                    path.join(settings.BASE_DIR,
                              'horarispompeu/settings_private.py'))
                message += 'Uploaded settings_private.py to S3\n'
                supervisord_config = Key(bucket)
                supervisord_config.key = '/{}/supervisord_horarispompeu.conf'.\
                    format(now)
                supervisord_config.set_contents_from_filename(
                    settings.SUPERVISORD_CONFIG)
                message += 'Uploaded supervisor conf to S3\n'
                nginx_config = Key(bucket)
                nginx_config.key = '/{}/nginx_horarispompeu'.format(now)
                nginx_config.set_contents_from_filename(settings.NGINX_CONFIG)
                message += 'Uploaded nginx conf to S3\n'
            except:
                # If something goes wrong, email traceback
                end = time.time()
                message += traceback.format_exc()
                message += "Time employed: {} seconds\n".format(end - start)
                send_mail(
                    "[HP] [UPDATE] [KO] {}".format(now),
                    message,
                    "horarispompeu@gmail.com",
                    [admin[1] for admin in settings.ADMINS],
                    True
                )
                self.stderr.write("DONE. backup KO")
                return
        # Parse subjects in search for new aliases
        update = Popen([path.join(settings.BASE_DIR, "./manage.py"),
                        "update"], stdout=PIPE, stderr=PIPE)
        output, error = update.communicate()
        if output:
            message += output
        if error:
            message += error
        if update.returncode:  # If return code != 0, something wrong
            end = time.time()
            message += "Time employed: {} seconds\n".format(end - start)
            send_mail(
                "[HP] [UPDATE] [KO] {}".format(now),
                message,
                "horarispompeu@gmail.com",
                [admin[1] for admin in settings.ADMINS],
                True
            )
            self.stdout.write(output)
            self.stderr.write(error)
            self.stderr.write("DONE. update KO")
            return
        # If everything has gone OK
        end = time.time()
        message += "Time employed: {} seconds\n".format(end - start)
        send_mail(
            "[HP] [UPDATE] [OK] {}".format(now),
            message,
            "horarispompeu@gmail.com",
            [admin[1] for admin in settings.ADMINS],
            True
        )
        self.stdout.write(output)
        self.stderr.write(error)
        self.stdout.write("DONE. ALL OK")
