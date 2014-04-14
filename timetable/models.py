# encoding: utf-8

# Copyright (C) 2013  Octavi Font <octavi.fs@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import unicode_literals
from django.db import models


class Faculty(models.Model):
    """
    Stores the name of the faculty giving the classes. The name should be unique
    within a university, so it is used as the primary key for the model.
    e.g. ESUP is the faculty name of the engineering section in the UPF.
    """
    name = models.CharField(max_length=100, primary_key=True)
    name_key = models.CharField(max_length=10)

    class Meta:
        verbose_name_plural = "Faculties"  # admin will show correct plural
        unique_together = ("name", "name_key")

    def __unicode__(self):
        return self.name


class Degree(models.Model):
    """
    Stores the name of a degree. A degree is linked to some faculty.
    The pair degree name and faculty are unique.
    A degree has a series of subjects, each one given on a specific term and
    year. Various degrees can share subjects.
    """
    faculty = models.ForeignKey(Faculty)
    name = models.CharField(max_length=100)
    name_key = models.CharField(max_length=10)
    plan_key = models.CharField(max_length=10)

    class Meta:
        unique_together = ("faculty", "name", "name_key", "plan_key")
        ordering = ["name"]

    def __unicode__(self):
        rep = [
            "<Degree object>",
            "faculty: {0}".format(repr(self.faculty)),
            "name: {0}".format(repr(self.name)),
        ]
        return "\n".join(rep)


class Subject(models.Model):
    """
    Stores the name of the subject.
    Subjects are linked to a degree. Still, there are subjects that may be
    taught in multiple degrees, even though they are different entries. We will
    simply duplicate the information.
    """
    degree = models.ForeignKey(Degree)
    name = models.CharField(max_length=100)
    name_key = models.CharField(max_length=10)

    class Meta:
        unique_together = ("degree", "name", "name_key")
        ordering = ("name", "degree")

    def __unicode__(self):
        return "{0} a {1}".format(self.name, self.degree.name)


class AcademicYear(models.Model):
    """
    AcademicYear refers to the specific year the lessons are taking place.
    E.g. 2013-14, 2014-15...
    """
    year = models.CharField(max_length=100, primary_key=True)
    year_key = models.CharField(max_length=10)

    class Meta:
        unique_together = ("year", "year_key")

    def __unicode__(self):
        return self.year


class Lesson(models.Model):
    """
    Lesson is a class, from an specific subject, taking
    place on a specific day, for some group.
    """
    subject = models.ForeignKey(Subject)
    group = models.CharField(max_length=50)
    date_start = models.DateTimeField('lesson start')
    date_end = models.DateTimeField('lesson end')
    academic_year = models.ForeignKey(AcademicYear)
    term = models.CharField(max_length=50)
    entry = models.TextField(blank=True)
    location = models.CharField(max_length=50, blank=True)
    creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-academic_year", "date_start", "subject", "group")
        unique_together = ("subject", "group", "date_start", "date_end",
                           "academic_year", "term", "entry", "location")

    def __unicode__(self):
        rep = [
            "<Lesson object>"
            "subject: " + repr(self.subject.name if self.subject else None),
            "entry: " + repr(self.entry),
            "date_start: " + repr(self.date_start),
            "date_end: " + repr(self.date_end),
        ]
        return '\n'.join(rep)

    def __key(self):
        return (self.subject.id, self.group, self.date_start, self.date_end,
                self.academic_year.id, self.term, self.entry, self.location)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if type(other) is type(self):
            return other.__key() == self.__key()
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


class DegreeSubject(models.Model):
    """
    This model links a subject with a degree. It also stores some additional
    information, like the academic term, year or group.
    """
    subject = models.ForeignKey(Subject)
    degree = models.ForeignKey(Degree)
    academic_year = models.ForeignKey(AcademicYear)
    course = models.CharField(max_length=50)
    course_key = models.CharField(max_length=10)
    term = models.CharField(max_length=50)
    term_key = models.CharField(max_length=10)
    group = models.CharField(max_length=50)
    group_key = models.CharField(max_length=10)

    class Meta:
        ordering = ("-academic_year", "course", "term", "subject", "group")
        unique_together = ("subject", "degree", "academic_year", "course",
                           "term", "group", "course_key", "term_key",
                           "group_key")

    def __unicode__(self):
        return " ".join([self.subject.name, self.degree.name, self.course,
                         self.term])

    def lessons(self):
        """
        Returns QuerySet with the lessons associated to the DegreeSubject
        """
        return Lesson.objects.filter(
            subject=self.subject,
            academic_year=self.academic_year,
            group=self.group,
            term=self.term
        )


class Calendar(models.Model):
    """
    Stores the reference to a calendar .ics file, with an arbitrary number of
    degree_subjects. There is the name of the file, the path to the file and
    a ManyToManyField that links to the degree_subjects that conform the
    calendar.
    """
    name = models.CharField(max_length=128, primary_key=True, blank=False)
    file = models.FileField(upload_to='.')
    degree_subjects = models.ManyToManyField(DegreeSubject)
