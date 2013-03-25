# encoding: utf-8
from __future__ import unicode_literals
from django.contrib import admin
from timetable.models import *


# Register all classes from the model to the admin panel
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'faculty']


class SubjectAliasAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject']

admin.site.register(Faculty)
admin.site.register(Degree)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(SubjectDuplicate)
admin.site.register(SubjectAlias, SubjectAliasAdmin)
admin.site.register(AcademicYear)
admin.site.register(Class)
admin.site.register(DegreeSubject)
admin.site.register(Calendar)
