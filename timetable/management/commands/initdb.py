# encoding: utf-8
from __future__ import unicode_literals
from django.core.management.base import NoArgsCommand

from timetable.models import Faculty, Degree, AcademicYear


class Command(NoArgsCommand):
    help = "Inserts basic initial data onto the DB."

    def handle_noargs(self, **options):
        esup = Faculty(name='ESUP')
        esup.save()
        Degree(
            faculty=esup,
            name='Grau en Enginyeria de Sistemes Audiovisuals'
        ).save()
        Degree(
            faculty=esup,
            name='Grau en Enginyeria de Telemàtica'
        ).save()
        Degree(
            faculty=esup,
            name='Grau en Enginyeria en Informàtica'
        ).save()
        AcademicYear(year='2012-13').save()
