from django.db import models


# Create your models here.
class Class(models.Model):
    subject = models.CharField(max_length=100)
    group = models.CharField(max_length=50)
    subgroup = models.CharField(max_length=50, blank=True)
    kind = models.CharField(max_length=50)
    room = models.CharField(max_length=50)
    date_start = models.DateTimeField('class start')
    date_end = models.DateTimeField('class end')

    def __unicode__(self):
        rep = "<Class object>\n"
        rep += "subject: " + repr(self.subject) + "\n"
        rep += "kind: " + repr(self.kind) + "\n"
        rep += "group: " + repr(self.group) + "\n"
        rep += "room: " + repr(self.room) + "\n"
        rep += "date_start: " + repr(self.date_start) + "\n"
        rep += "date_end: " + repr(self.date_end) + "\n"
        return rep


class DegreeSubject(models.Model):
    degree = models.CharField(max_length=100)  # Restrict input values here
    year = models.CharField(max_length=50)  # Restrict input values here
    term = models.CharField(max_length=50)  # Restrict input values here
    subject = models.ForeignKey(Class, to_field='subject')
    group = models.ForeignKey(Class, to_field='group')


class Calendar:
    calendar = models.FileField
    degree_subject = models.ManyToManyField(DegreeSubject)
