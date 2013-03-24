from django.db import models


class Faculty(models.Model):
    name = models.CharField(max_length=100, primary_key=True)

    class Meta:
        verbose_name_plural = 'Faculties'  # admin will show correct plural


class Degree(models.Model):
    faculty = models.ForeignKey(Faculty)
    name = models.CharField(max_length=100)

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


class SubjectAlias(models.Model):
    '''Links a subject alias to its 'official' name.
    Parsed data is not always accurate with subject names, so to solve
    inconsistencies, this model will link those mispellings with the actual
    subject.
    '''
    name = models.CharField(max_length=100)
    subject = models.ForeignKey(Subject)

    class Meta:
        verbose_name_plural = 'Subject aliases'


class Year(models.Model):
    name = models.CharField(max_length=100, primary_key=True)


GROUP_CHOICES = (
    ("GRUP 1", "GRUP 1"),
    ("GRUP 2", "GRUP 2"),
)


class Class(models.Model):
    subject = models.ForeignKey(Subject, blank=True)
    group = models.CharField(max_length=50, choices=GROUP_CHOICES, blank=True)
    subgroup = models.CharField(max_length=50, blank=True)
    kind = models.CharField(max_length=50, blank=True)
    room = models.CharField(max_length=50, blank=True)
    date_start = models.DateTimeField('class start', blank=True)
    date_end = models.DateTimeField('class end', blank=True)
    year = models.ForeignKey(Year)
    raw_entry = models.TextField()

    class Meta:
        verbose_name_plural = 'Classes'

    def __unicode__(self):
        rep = [
            "<Class object>"
            "subject: " + repr(self.subject),
            "kind: " + repr(self.kind),
            "group: " + repr(self.group),
            "room: " + repr(self.room),
            "date_start: " + repr(self.date_start),
            "date_end: " + repr(self.date_end),
        ]
        return '\n'.join(rep)


class DegreeSubject(models.Model):
    TERM_CHOICES = (
        ('1r Trimestre', '1r Trimestre'),
        ('2n Trimestre', '2n Trimestre'),
        ('3r Trimestre', '3r Trimestre'),
    )
    subject = models.ForeignKey(Subject)
    degree = models.ForeignKey(Degree)
    year = models.ForeignKey(Year)
    term = models.CharField(max_length=50, choices=TERM_CHOICES)
    group = models.CharField(max_length=50, choices=GROUP_CHOICES)


class Calendar(models.Model):
    calendar = models.FileField(upload_to='.')
    degree_subject = models.ManyToManyField(DegreeSubject)
