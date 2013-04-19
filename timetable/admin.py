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
# limitations under the License.from __future__ import unicode_literals

from django.contrib import admin
from timetable.models import *


# Register all classes from the model to the admin panel
class SubjectAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'faculty']


class SubjectAliasAdmin(admin.ModelAdmin):
    search_fields = ['subject__name', 'name']
    list_display = ['name', 'subject']


class DegreeSubjectAdmin(admin.ModelAdmin):
    def subject_name(self, degreesubject):
        return degreesubject.subject.name

    def subject_faculty(self, degreesubject):
        return degreesubject.subject.faculty

    def degree_name(self, degreesubject):
        return degreesubject.degree.name

    search_fields = ['subject__name', 'degree__name']
    list_display = ['subject_name', 'subject_faculty', 'degree_name', 'year',
                    'term', 'group', 'academic_year']


class LessonAdmin(admin.ModelAdmin):
    def subject_name(self, lesson):
        return lesson.subject.name

    def subject_faculty(self, lesson):
        return lesson.subject.faculty

    search_fields = ['id', 'subject__name']
    list_display = ['subject_name', 'subject_faculty', 'kind', 'group',
                    'subgroup', 'room', 'date_start', 'date_end']
    date_hierarchy = 'date_start'
    list_filter = ['date_start', 'kind', 'group']


class CalendarAdmin(admin.ModelAdmin):
    def degree_subjects_list(self, calendar):
        subjects = map(
            lambda entry: u'{0} {1}'.format(*entry.values()),
            calendar.degree_subjects.all().values(
                'subject__name', 'group'
            ).distinct()
        )
        return u"\n".join(subjects)

    readonly_fields = ('degree_subjects_list',)
    fields = ['name', 'file', 'degree_subjects_list']
    list_display = ['name', 'file', 'degree_subjects_list']


class LessonActionAdmin(admin.ModelAdmin):
    def lesson_id(self, lessonaction):
        return lessonaction.lesson.id

    def lesson_subject(self, lessonaction):
        return lessonaction.lesson.subject.name

    def lesson_group(self, lessonaction):
        return lessonaction.lesson.group

    def lesson_subgroup(self, lessonaction):
        return lessonaction.lesson.subgroup

    def lesson_kind(self, lessonaction):
        return lessonaction.lesson.kind

    def lesson_room(self, lessonaction):
        return lessonaction.lesson.room

    def lesson_date_start(self, lessonaction):
        return lessonaction.lesson.date_start

    def lesson_date_end(self, lessonaction):
        return lessonaction.lesson.date_end

    def lesson_academic_year(self, lessonaction):
        return lessonaction.lesson.academic_year

    def lesson_raw_entry(self, lessonaction):
        return lessonaction.lesson.raw_entry

    # Necessary since auto_now_add=True in the models
    fields = ['date', 'lesson_id', 'lesson_subject', 'lesson_group',
              'lesson_subgroup', 'lesson_kind', 'lesson_room',
              'lesson_date_start', 'lesson_date_end', 'lesson_academic_year',
              'lesson_raw_entry']
    readonly_fields = fields
    list_display = fields


admin.site.register(Faculty)
admin.site.register(Degree)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(SubjectDuplicate)
admin.site.register(SubjectAlias, SubjectAliasAdmin)
admin.site.register(AcademicYear)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(DegreeSubject, DegreeSubjectAdmin)
admin.site.register(Calendar, CalendarAdmin)
admin.site.register(LessonInsert, LessonActionAdmin)
admin.site.register(LessonDelete, LessonActionAdmin)
admin.site.register(LessonArchive, LessonAdmin)
