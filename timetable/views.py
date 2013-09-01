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
# limitations under the License.

from __future__ import unicode_literals
from django.shortcuts import render
from django.template import Context, loader
from django.db.models import Q
import operator
import hashlib
from django.core.files.base import ContentFile
import os
import subprocess

from timetable.models import *
import timetable.calendar


# Create your views here.
def index(request):
    return render(request, 'index.html')


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
    year_degree_subjects = {}
    for degree_subject in degree_subjects:
        year_degree_subjects.setdefault(degree_subject['year'], []).append(degree_subject)
    context = {'year_degree_subjects': sorted(year_degree_subjects.iteritems())}
    return render(request, 'subject.html', context)


def calendar(request):
    academic_year = AcademicYear.objects.get(pk='2012-13')
    # degree_subjects contains a list with strings with the format
    # {subject_id}_{group}
    raw_selected_subjects = request.POST.getlist('degree_subject')
    raw_selected_subjects.sort()
    string_selected_subjects = "\n".join(raw_selected_subjects)
    # The calendar will have, for its filename, the SHA1 hash of the sorted
    # pairs of (subject_id, group) returned by the selection form
    subjects_hash = hashlib.sha1(string_selected_subjects).hexdigest()
    calendar = None
    try:
        calendar = Calendar.objects.get(pk=subjects_hash)
    except Calendar.DoesNotExist:
        calendar = Calendar(name=subjects_hash)
        selected_subjects = \
            [(lambda (s_id, group): (int(s_id), group))(e.split('_')) for e in
             request.POST.getlist('degree_subject')]
        if not selected_subjects:
            # TODO:
            # Throw some error when selectedsubjects has no subjects!
            # or handle it on the subject view (or both)
            pass
        q_list = []
        for subject_id, group in selected_subjects:
            q = Q(subject=subject_id, group=group, academic_year=academic_year)
            q_list.append(q)
        subjects_group_filter = reduce(operator.or_, q_list)
        lessons = Lesson.objects.filter(subjects_group_filter)
        degree_subjects = DegreeSubject.objects.filter(subjects_group_filter)
        calendar.file.save(calendar.name + '.ics',
                           ContentFile(timetable.calendar.generate(lessons)))
        calendar.degree_subjects.add(*degree_subjects)
    finally:
        context = {
            'calendar_url': calendar.file.url,
            'calendar_name': calendar.name
        }
        return render(request, 'calendar.html', context)


def subscription(request):
    email = "--email={}".format(request.POST["email"])
    password = "--password={}".format(request.POST["password"])
    calendar = "--calendar={}".format(request.POST["calendar"])
    result = subprocess.call(["casperjs", "/Users/octavi/projects/horarispompeu/casperjs/addICSCal.js", email, password, calendar])
    return render(request, 'subscription_result.html', {'result': result})
