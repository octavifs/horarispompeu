# encoding: utf-8
from __future__ import unicode_literals
from django.contrib import admin
from timetable.models import *


# Register all classes from the model to the admin panel
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'faculty']


class SubjectAliasAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject']


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

admin.site.register(Faculty)
admin.site.register(Degree)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(SubjectDuplicate)
admin.site.register(SubjectAlias, SubjectAliasAdmin)
admin.site.register(AcademicYear)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(DegreeSubject)
admin.site.register(Calendar)
