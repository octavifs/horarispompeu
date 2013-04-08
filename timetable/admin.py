# encoding: utf-8
from __future__ import unicode_literals
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

    search_fields = ['subject__name']
    list_display = ['subject_name', 'subject_faculty', 'kind', 'group',
                    'subgroup', 'room', 'date_start', 'date_end']
    date_hierarchy = 'date_start'
    list_filter = ['date_start', 'kind', 'group']


class CalendarAdmin(admin.ModelAdmin):
    def degree_subjects_list(self, calendar):
        subjects = map(
            lambda entry: '{0} {1}'.format(*entry.values()),
            calendar.degree_subjects.all()
                .values('subject__name', 'group').distinct()
        )
        return "\n".join(subjects)

    readonly_fields = ('degree_subjects_list',)
    fields = ['name', 'file', 'degree_subjects_list']
    list_display = ['name', 'file', 'degree_subjects_list']


admin.site.register(Faculty)
admin.site.register(Degree)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(SubjectDuplicate)
admin.site.register(SubjectAlias, SubjectAliasAdmin)
admin.site.register(AcademicYear)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(DegreeSubject, DegreeSubjectAdmin)
admin.site.register(Calendar, CalendarAdmin)
