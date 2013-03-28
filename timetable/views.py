from __future__ import unicode_literals
from django.http import HttpResponse
from django.shortcuts import render
from django.template import Context, loader
from django.db.models import Q
import operator

from timetable.models import *


# Create your views here.
def index(request):
    subject_list = Subject.objects.all()
    template = loader.get_template('index.html')
    context = Context({
        'subject_list': subject_list
    })
    return HttpResponse(template.render(context))


def degree(request):
    faculty = Faculty.objects.get(pk='ESUP')
    degree_list = Degree.objects.filter(faculty=faculty)
    context = {'degree_list': degree_list}
    return render(request, 'degree.html', context)


def year(request):
    year_choices = [entry[0] for entry in DegreeSubject.YEAR_CHOICES]
    degree_list = dict((Degree.objects.get(pk=key), year_choices)
                       for key in request.POST.getlist('degree'))
    context = {'degree_list': degree_list}
    return render(request, 'year.html', context)


def subject(request):
    academic_year = AcademicYear.objects.get(pk='2012-13')
    degree_year = request.POST.getlist('degree_year')
    courses = []
    for entry in degree_year:
        degree_id, course = entry.split('_')
        degree = Degree.objects.get(pk=degree_id)
        courses.append((degree, course))
    degree_subjects = []
    q_list = []
    for degree, course in courses:
        q = Q(degree=degree, year=course, academic_year=academic_year)
        q_list.append(q)
    degree_subjects = DegreeSubject.objects.filter(
        reduce(operator.or_, q_list)
    ).order_by(
        'term',
        'subject',
        'group',
    )
    distinct_subjects = set()
    distinct_degree_subjects = []
    for degree_subject in degree_subjects:
        if (degree_subject.subject, degree_subject.group) in distinct_subjects:
            continue
        distinct_degree_subjects.append(degree_subject)
        distinct_subjects.add((degree_subject.subject, degree_subject.group))
    context = {'degree_subjects': distinct_degree_subjects}
    return render(request, 'subject.html', context)


def calendar(request):
    return HttpResponse('Work in progress')
