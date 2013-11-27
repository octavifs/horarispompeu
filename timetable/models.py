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

    class Meta:
        verbose_name_plural = 'Faculties'  # admin will show correct plural

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

    class Meta:
        unique_together = ("faculty", "name")
        ordering = ["name"]

    def __unicode__(self):
        rep = [
            "<Degree object>",
            "faculty: {0}".format(repr(self.faculty)),
            "name: {0}".format(repr(self.name)),
        ]
        return '\n'.join(rep)


class Subject(models.Model):
    """
    Stores the name of the subject.
    A subject is taught by a faculty. Subjects are not linked to any degree in
    particular, since there are many degrees that share the same subjects.
    A pair of subject name and faculty are unique.
    """
    faculty = models.ForeignKey(Faculty)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ("faculty", "name")
        ordering = ("name", "faculty")

    def __unicode__(self):
        return "{0} a {1}".format(self.name, self.faculty)


class SubjectAlias(models.Model):
    """
    Links a subject alias to its 'official' name.
    Parsed data is not always accurate with subject names, so to solve
    inconsistencies, this model will link those mispellings with the actual
    subject object.
    """
    name = models.CharField(max_length=100)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True,
                                blank=True)

    class Meta:
        verbose_name_plural = 'Subject aliases'
        unique_together = ("name", "subject")
        ordering = ("subject", "name")


class AcademicYear(models.Model):
    """
    AcademicYear refers to the specific year the lessons are taking place.
    E.g. 2013-14, 2014-15...
    """
    year = models.CharField(max_length=100, primary_key=True)

    def __unicode__(self):
        return self.year


# Since there are only 2 groups available, I put them in a tuple instead of a
# model
GROUP_CHOICES = (
    ("GRUP 1", "GRUP 1"),
    ("GRUP 2", "GRUP 2"),
)


class Lesson(models.Model):
    """
    Lesson is a class, from an specific subject, taking
    place on a specific day, for some group.
    """
    subject = models.ForeignKey(Subject, null=True, blank=True)
    group = models.CharField(max_length=50, choices=GROUP_CHOICES, blank=True)
    date_start = models.DateTimeField('lesson start', null=True, blank=True)
    date_end = models.DateTimeField('lesson end', null=True, blank=True)
    academic_year = models.ForeignKey(AcademicYear)
    entry = models.TextField(blank=True)
    raw_entry = models.TextField()
    creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-academic_year", "date_start", "subject", "group")
        unique_together = ("subject", "group", "entry", "date_start",
                           "date_end", "academic_year")

    def __unicode__(self):
        rep = [
            "<Lesson object>"
            "subject: " + repr(self.subject.name if self.subject else None),
            "entry: " + repr(self.entry),
            "date_start: " + repr(self.date_start),
            "date_end: " + repr(self.date_end),
        ]
        return '\n'.join(rep)

    def complete(self):
        return bool(self.subject and self.entry)
    complete.boolean = True


class DegreeSubject(models.Model):
    """
    This model links a subject with a degree. It also stores some additional
    information, like the academic term, year or group.
    """
    TERM_CHOICES = (
        ('1r Trimestre', '1r Trimestre'),
        ('2n Trimestre', '2n Trimestre'),
        ('3r Trimestre', '3r Trimestre'),
    )
    YEAR_CHOICES = (
        ("1r", "1r"),
        ("2n", "2n"),
        ("3r", "3r"),
        ("4t", "4t"),
        ("optatives", "optatives"),
    )
    subject = models.ForeignKey(Subject)
    degree = models.ForeignKey(Degree)
    academic_year = models.ForeignKey(AcademicYear)
    year = models.CharField(max_length=50, choices=YEAR_CHOICES)
    term = models.CharField(max_length=50, choices=TERM_CHOICES)
    group = models.CharField(max_length=50, choices=GROUP_CHOICES)

    class Meta:
        ordering = ("-academic_year", "year", "term", "subject", "group")
        unique_together = ("subject", "degree", "academic_year", "year", "term",
                           "group")

    def __unicode__(self):
        return " ".join([self.subject.name, self.degree.name, self.year, self.term])

    def lessons(self):
        """
        Returns QuerySet with the lessons associated to the DegreeSubject
        """
        return Lesson.objects.filter(
            subject=self.subject,
            academic_year=self.academic_year,
            group=self.group
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
