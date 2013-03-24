# encoding: utf-8
from __future__ import unicode_literals
from django.core.management.base import NoArgsCommand
from django.db import IntegrityError
import requests
from bs4 import BeautifulSoup
from timetable.models import Faculty, Subject, SubjectAlias


# Faculty names
ESUP = 'ESUP'


class Command(NoArgsCommand):
    help = "Parse subjects from the faculties and put them into the Database."

    # Dictionary with faculties and list with the study program of each degree
    faculties = {
        ESUP: [
            "http://www.upf.edu/pra/3377/",  # Informàtica
            "http://www.upf.edu/pra/3376/",  # Telemàtica
            "http://www.upf.edu/pra/3375/",  # Audiovisuals
        ],
    }

    def handle_noargs(self, **options):
        # First of all, we add any missing faculty to the database
        for faculty in self.faculties:
            try:
                Faculty.objects.get(name=faculty)
            except Faculty.DoesNotExist:
                entry = Faculty(faculty)
                entry.save()
        # For each faculty, we download its list of subjects per degree
        for faculty, degreeprograms in self.faculties.iteritems():
            try:
                for program in degreeprograms:
                    html = requests.get(program).text
                    if faculty == ESUP:
                        self.parse_esup_html_into_subjects(html)
                    else:
                        print "Parsing HTML from {0} undefined".format(faculty)
            except requests.ConnectionError, e:
                print "Error: Server unreachable"
                raise e
            except Exception, e:
                raise e

    def parse_esup_html_into_subjects(self, html):
        # Gets ESUP faculty object from DB
        try:
            faculty = Faculty.objects.get(name=ESUP)
        except Faculty.DoesNotExist, e:
            raise e
        # Parses html.
        # Subject names are inside <li> tags with the class 'sumari'
        # Like this:
        # <li class="sumari">
        #   <a href="/pra/3376/21293.pdf" title="&nbsp;21293">21293</a>
        #   &nbsp;Introducció a les TIC
        # </li>
        html = BeautifulSoup(html)
        for entry in html.find_all(name='li', attrs={'class': 'sumari'}):
            # Gets the entry and deletes the subject code (5 digit code)
            # Each entry looks like this:
            # 22683 Sistemes Interactius
            subject_name = entry.text[6:]
            # Saves subject to the DB. If subject had already been saved,
            # retrieve it from the DB
            try:
                subject = Subject(faculty=faculty, name=subject_name)
                subject.save()
            except IntegrityError:
                subject = Subject.objects.filter(faculty=faculty,
                                                 name=subject_name)[0]
            # Creates an alias linking subject_name with the subject tuple
            # More aliases will be added manually later
            # If alias had already been saved, do nothing
            try:
                subject_alias = SubjectAlias(name=subject_name, subject=subject)
                subject_alias.save()
            except IntegrityError:
                pass
