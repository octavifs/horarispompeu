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
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.core import serializers
from django.views.decorators.http import require_http_methods
from django.db.models.query import QuerySet
from django.db.models import Model
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


@require_http_methods(["GET"])
def subject(request, pk=None):
    R = request.REQUEST
    if not pk:
        faculty = Faculty.objects.get(pk='ESUP')
        results = Subject.objects.filter(faculty=faculty)
        if 'name' in R:
            results = results.filter(name__contains=R['name'])
        return jsonify(results)
    try:
        return jsonify(Subject.objects.get(pk=pk))
    except Subject.DoesNotExist:
        return HttpResponseNotFound("Unknown key")


@require_http_methods(["GET"])
def course(request, pk=None):
    R = request.REQUEST
    if not pk:
        academic_year = AcademicYear.objects.latest('year')
        results = DegreeSubject.objects.filter(academic_year=academic_year)
        if 'subject' in R:
            results = results.filter(subject=R['subject'])
        if 'degree' in R:
            results = results.filter(degree=R['degree'])
        if 'year' in R:
            results = results.filter(year=R['year'])
        if 'term' in R:
            results = results.filter(term=R['term'])
        if 'group' in R:
            results = results.filter(group=R['group'])
        return jsonify(results)
    try:
        return jsonify(DegreeSubject.objects.get(pk=pk))
    except DegreeSubject.DoesNotExist:
        return HttpResponseNotFound("Unknown key")


@require_http_methods(["GET"])
def lesson(request, pk):
    try:
        degree_subject = DegreeSubject.objects.get(pk=pk)
        return jsonify(degree_subject.lessons())
    except DegreeSubject.DoesNotExist:
        return HttpResponseNotFound("Unknown key")


@require_http_methods(["POST"])
def subscription(request):
    R = request.REQUEST
    # First, deal with invalid inputs:
    if (email not in R) or (password not in R) or (calendar not in R):
        return HttpResponseBadRequest("Missing parameters")
    # Once input is seemingly valid render the view:
    email = "--email={}".format(R["email"])
    password = "--password={}".format(R["password"])
    calendar = "--calendar={}".format(R["calendar"])
    result = subprocess.call(["casperjs", "casperjs/addICSCal.js", email, password, calendar])
    return jsonify({'result': result})
