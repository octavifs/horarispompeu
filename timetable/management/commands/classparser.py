# encoding: utf-8
from __future__ import unicode_literals
from django.core.management.base import NoArgsCommand
from django.db import IntegrityError
import requests
from _esup_timetable_data import *
import _parser as parser


class Command(NoArgsCommand):
    help = "Parse classes and subjects from the ESUP degrees"

    def handle_noargs(self, **options):
        for degree, years in COMPULSORY_SUBJECTS_TIMETABLES.iteritems():
            for year, terms in years.iteritems():
                for term, groups in terms.iteritems():
                    for group, url in groups:
                        print url
                        html = requests.get(url).text
                        self.parse(degree, year, term, group, html)
                        print ""
        for term, groups in OPTIONAL_SUBJECTS_TIMETABLES.iteritems():
            for group, url in groups:
                print url
                requests.get(url)
                print ""

    def parse(self, degree, year, term, group, html):
        classes = parser.parse(html)
        for entry in classes:
            print entry.raw_data
