# encoding: utf-8
from __future__ import unicode_literals
from django.core.management.base import NoArgsCommand
from django.db import IntegrityError
import requests
from bs4 import BeautifulSoup
from esup_timetable_data import *


class Command(NoArgsCommand):
    help = "Parse classes and subjects from the ESUP degrees"

    def handle_noargs(self, **options):
        for degree, years in COMPULSORY_SUBJECTS_TIMETABLES.iteritems():
            for year, terms in years.iteritems():
                for term, groups in terms.iteritems():
                    for group, url in groups:
                        print url
                        requests.get(url)
                        print ""
        for term, groups in OPTIONAL_SUBJECTS_TIMETABLES.iteritems():
            for group, url in groups:
                print url
                requests.get(url)
                print ""
