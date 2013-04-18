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
from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.db import IntegrityError


class Faculty(models.Model):
    name = models.CharField(max_length=100, primary_key=True)

    class Meta:
        verbose_name_plural = 'Faculties'  # admin will show correct plural

    def __unicode__(self):
        return self.name


class Degree(models.Model):
    faculty = models.ForeignKey(Faculty)
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]

    def __unicode__(self):
        rep = [
            "<Degree object>",
            "faculty: {0}".format(repr(self.faculty)),
            "name: {0}".format(repr(self.name)),
        ]
        return '\n'.join(rep)


class Subject(models.Model):
    faculty = models.ForeignKey(Faculty)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ("faculty", "name")
        ordering = ("name", "faculty")

    def __unicode__(self):
        return "{0} a {1}".format(self.name, self.faculty)


class SubjectDuplicate(models.Model):
    """Stores subjects that appear multiple times on the degree subject list
    under similar names.
    """
    faculty = models.ForeignKey(Faculty)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ("faculty", "name")
        ordering = ("name", "faculty")

    def __unicode__(self):
        return "{0} a {1}".format(self.name, self.faculty)


@receiver(post_delete, sender=Subject)
def _subject_delete(sender, instance, **kwargs):
    try:
        fields = {
            'faculty': instance.faculty,
            'name': instance.name,
        }
        print fields
        duplicate = SubjectDuplicate(**fields)
        duplicate.save()
    except IntegrityError, e:
        print e


class SubjectAlias(models.Model):
    '''Links a subject alias to its 'official' name.
    Parsed data is not always accurate with subject names, so to solve
    inconsistencies, this model will link those mispellings with the actual
    subject.
    '''
    name = models.CharField(max_length=100)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True,
                                blank=True)

    class Meta:
        verbose_name_plural = 'Subject aliases'
        unique_together = ("name", "subject")
        ordering = ("subject", "name")


class AcademicYear(models.Model):
    year = models.CharField(max_length=100, primary_key=True)

    def __unicode__(self):
        return self.year


GROUP_CHOICES = (
    ("GRUP 1", "GRUP 1"),
    ("GRUP 2", "GRUP 2"),
)


class LessonCommon(models.Model):
    subject = models.ForeignKey(Subject, null=True, blank=True)
    group = models.CharField(max_length=50, choices=GROUP_CHOICES, blank=True)
    subgroup = models.CharField(max_length=50, blank=True)
    kind = models.CharField(max_length=50, blank=True)
    room = models.CharField(max_length=50, blank=True)
    date_start = models.DateTimeField('lesson start', null=True, blank=True)
    date_end = models.DateTimeField('lesson end', null=True, blank=True)
    academic_year = models.ForeignKey(AcademicYear)
    raw_entry = models.TextField()

    class Meta:
        abstract = True
        ordering = ("-academic_year", "date_start", "subject", "group")

    def __unicode__(self):
        rep = [
            "<Lesson object>"
            "subject: " + repr(self.subject.name),
            "kind: " + repr(self.kind),
            "group: " + repr(self.group),
            "room: " + repr(self.room),
            "date_start: " + repr(self.date_start),
            "date_end: " + repr(self.date_end),
        ]
        return '\n'.join(rep)


class Lesson(LessonCommon):
    class Meta:
        verbose_name_plural = 'Lessons'
        # Don't allow duplicate entries
        unique_together = ("subject", "group", "subgroup", "kind", "room",
                           "date_start", "date_end", "academic_year")


class DegreeSubject(models.Model):
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
    name = models.CharField(max_length=128, primary_key=True, blank=False)
    file = models.FileField(upload_to='.')
    degree_subjects = models.ManyToManyField(DegreeSubject)


#
# Models and signals necessary to handle the archiving of added and deleted
# Lessons
#
class LessonArchive(LessonCommon):
    class Meta:
        verbose_name_plural = 'Lessons Archives'


class LessonInsert(models.Model):
    # Delete entry if Lesson is removed
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-date",)


class LessonDelete(models.Model):
    lesson = models.ForeignKey(LessonArchive, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-date",)


@receiver(post_save, sender=Lesson)
def _lesson_insert(sender, instance, **kwargs):
    try:
        inserted_record = LessonInsert(lesson=instance)
        inserted_record.save()
    except IntegrityError, e:
        print e


@receiver(post_delete, sender=Lesson)
def _lesson_delete(sender, instance, **kwargs):
    try:
        fields = {
            'subject': instance.subject,
            'group': instance.group,
            'subgroup': instance.subgroup,
            'kind': instance.kind,
            'room': instance.room,
            'date_start': instance.date_start,
            'date_end': instance.date_end,
            'academic_year': instance.academic_year,
            'raw_entry': instance.raw_entry
        }
        archived_lesson = LessonArchive(**fields)
        archived_lesson.save()
        deleted_record = LessonDelete(lesson=archived_lesson)
        deleted_record.save()
    except IntegrityError, e:
        print e


@receiver(post_delete, sender=LessonDelete)
def _lessondelete_delete(sender, instance, **kwargs):
    try:
        instance.lesson.delete()
    except IntegrityError, e:
        print e
    except LessonArchive.DoesNotExist:
        pass
