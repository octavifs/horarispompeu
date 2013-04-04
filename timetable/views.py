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
    degree_and_group_list = DegreeSubject.objects.filter(
        degree__in=request.POST.getlist('degree')
    ).order_by(
        'degree',
        'year',
        'group'
    ).values(
        'degree',
        'degree__name',
        'year',
        'group',
    ).distinct()
    degree_list = dict()
    for entry in degree_and_group_list:
        degree_list.setdefault(entry['degree__name'], []).append(entry)
    context = {'degree_list': degree_list}
    return render(request, 'year.html', context)


def subject(request):
    academic_year = AcademicYear.objects.get(pk='2012-13')
    degree_year = request.POST.getlist('degree_year')
    courses = []
    for entry in degree_year:
        degree_id, course, group = entry.split('_')
        courses.append((degree_id, course, group))
    degree_subjects = []
    q_list = []
    for degree, course, group in courses:
        q = Q(degree=degree, year=course, group=group,
              academic_year=academic_year)
        q_list.append(q)
    degree_subjects = DegreeSubject.objects.filter(
        reduce(operator.or_, q_list)
    ).order_by(
        'year',
        'subject__name',
    ).values(
        'subject',
        'subject__name',
        'group',
        'year'
    ).distinct()
    print degree_subjects
    context = {'degree_subjects': degree_subjects}
    return render(request, 'subject.html', context)


def calendar(request):
    return HttpResponse('Work in progress')
