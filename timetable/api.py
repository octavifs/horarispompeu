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
from django.http import HttpResponse, HttpResponseNotFound
from django.core import serializers
from django.views.decorators.http import require_http_methods
from django.db.models.query import QuerySet
from django.db.models import Model
from django.db.models import Q
import operator
import hashlib
from django.core.files.base import ContentFile
import os
import subprocess
import json
# from django.core.serializers.json import DjangoJSONEncoder

from timetable.models import *
import timetable.calendar


class ModelJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        return repr(obj)


class DjangoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        json_serializer = serializers.get_serializer("json")()
        if isinstance(obj, QuerySet):
            return json.loads(json_serializer.serialize(obj, ensure_ascii=False))
        if isinstance(obj, Model):
            return json.loads(json_serializer.serialize([obj], ensure_ascii=False))[0]
        return json.JSONEncoder.default(self, obj)


def jsonify(obj):
    """Returns HttpResponse with the JSON version of obj."""
    json_string = json.dumps(obj, cls=DjangoJSONEncoder, indent=2, ensure_ascii=False)
    return HttpResponse(json_string, content_type="application/json; charset=utf-8")


# Create your views here.
@require_http_methods(["GET"])
def faculty(request, pk=None):
    if not pk:
        return jsonify(Faculty.objects.all())
    try:
        return jsonify(Faculty.objects.get(pk=pk))
    except Faculty.DoesNotExist:
        return HttpResponseNotFound("Unknown key")


@require_http_methods(["GET"])
def degree(request, pk=None):
    R = request.REQUEST
    if not pk:
        faculty = Faculty.objects.get(pk='ESUP')
        results = Degree.objects.filter(faculty=faculty)
        if 'name' in R:
            results = results.filter(name__contains=R['name'])
        return jsonify(results)
    try:
        return jsonify(Degree.objects.get(pk=pk))
    except Degree.DoesNotExist:
        return HttpResponseNotFound("Unknown key")


def year(request):
    # First, deal with invalid inputs:
    if (request.method == 'GET' or
        not request.POST.getlist('degree')
    ):
        # This will raise a 500 error page on production
        return render(request, '500.html', {})
    # Once input is seemingly valid (the list may still contain invalid degree ids), retrieve years and groups:
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


def lesson(request):
    return HttpResponse("")


def subject(request):
    # First, deal with invalid inputs:
    if (request.method == 'GET' or
        not request.POST.getlist('degree_year')
    ):
        # This will raise a 500 error page on production
        return render(request, '500.html', {})
    # Once input is seemingly valid render the view:
    academic_year = AcademicYear.objects.latest('pk')
    degree_year = request.POST.getlist('degree_year')
    courses = []
    for entry in degree_year:
        degree_id, course, group = entry.split('_')
        courses.append((degree_id, course, group))
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
    # First, deal with invalid inputs:
    if (request.method == 'GET' or
        not request.POST.getlist('degree_subject')
    ):
        # This will raise a 500 error page on production
        return render(request, '500.html', {})
    # Once input is seemingly valid render the view:
    academic_year = AcademicYear.objects.latest('pk')
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
    # First, deal with invalid inputs:
    if (request.method == 'GET' or
        not request.POST["email"] or
        not request.POST["password"] or
        not request.POST["calendar"]
    ):
        # This will render a 500 error page on production
        return render(request, '500.html', {})
    # Once input is seemingly valid render the view:
    email = "--email={}".format(request.POST["email"])
    password = "--password={}".format(request.POST["password"])
    calendar = "--calendar={}".format(request.POST["calendar"])
    result = subprocess.call(["casperjs", "casperjs/addICSCal.js", email, password, calendar])
    return render(request, 'subscription_result.html', {'result': result})
