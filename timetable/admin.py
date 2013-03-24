from django.contrib import admin
from timetable.models import *

# Register all classes from the model to the admin panel
admin.site.register(Faculty)
admin.site.register(Degree)
admin.site.register(Subject)
admin.site.register(SubjectAlias)
admin.site.register(Year)
admin.site.register(Class)
admin.site.register(DegreeSubject)
admin.site.register(Calendar)
