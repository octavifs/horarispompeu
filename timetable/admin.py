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
    def degree_name(self, subject):
        return subject.degree.name
    search_fields = ['name']
    list_display = ['name', 'degree_name']


class DegreeAdmin(admin.ModelAdmin):
    search_fields = ['faculty', 'name', 'name_key']
    list_display = ['faculty', 'name', 'name_key', 'plan_key']


class DegreeSubjectAdmin(admin.ModelAdmin):
    def subject_name(self, degreesubject):
        return degreesubject.subject.name

    def degree_faculty(self, degreesubject):
        return degreesubject.degree.faculty.name

    def degree_name(self, degreesubject):
        return degreesubject.degree.name

    search_fields = ['subject__name', 'degree__name']
    list_display = ['subject_name', 'degree_faculty', 'degree_name', 'course',
                    'term', 'group', 'academic_year']


class LessonAdmin(admin.ModelAdmin):
    def subject_name(self, lesson):
        return lesson.subject.name

    def subject_faculty(self, lesson):
        return lesson.subject.degree.faculty

    search_fields = ['id', 'subject__name']
    list_display = ['subject_name', 'subject_faculty', 'entry',
                    'date_start', 'date_end', 'creation']
    date_hierarchy = 'date_start'
    list_filter = ['date_start', 'subject__name', 'creation']
    save_as = True


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


admin.site.register(Faculty)
admin.site.register(Degree, DegreeAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(AcademicYear)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(DegreeSubject, DegreeSubjectAdmin)
admin.site.register(Calendar, CalendarAdmin)
