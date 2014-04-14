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

import operator
import hashlib
import subprocess

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.core.files.base import ContentFile

from django.conf import settings
from timetable.models import *
import timetable.calendar
from timetable.forms import ContactForm


def degree(request):
    faculty = Faculty.objects.get(pk='ESUP')
    degree_list = Degree.objects.filter(faculty=faculty)
    context = {'degree_list': degree_list}
    return render(request, 'degree.html', context)


def year(request):
    # First, deal with invalid inputs:
    if (
        not request.session.get('degree') and
        not request.POST.getlist('degree')
    ):
        # This will raise a 500 error page on production
        return render(request, '500.html', {'term': settings.TERM})
    # Save POST parameters to cookie
    if request.method == 'POST':
        request.session['degree'] = request.POST.getlist('degree')
    # Once input is seemingly valid (the list may still contain invalid degree ids), retrieve years and groups:
    degree_and_group_list = DegreeSubject.objects.filter(
        degree__in=request.session['degree']
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
    degree_list = {}
    for entry in degree_and_group_list:
        degree_list.setdefault(entry['degree__name'], []).append(entry)
    context = {'degree_list': degree_list}
    return render(request, 'year.html', context)


def subject(request):
    # First, deal with invalid inputs:
    if (
        not request.session.get('degree_year') and
        not request.POST.getlist('degree_year')
    ):
        # This will raise a 500 error page on production
        return render(request, '500.html', {'term': settings.TERM})
    # Once input is seemingly valid render the view:
    academic_year = AcademicYear.objects.get(year=settings.ACADEMIC_YEAR)
    # Save POST parameters to cookie
    if request.method == 'POST':
        request.session['degree_year'] = request.POST.getlist('degree_year')
    degree_year = request.session['degree_year']
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
    context = {
        'year_degree_subjects': sorted(year_degree_subjects.iteritems()),
    }
    return render(request, 'subject.html', context)


def calendar(request):
    # First, deal with invalid inputs:
    if (
        not request.session.get('degree_subject') and
        not request.POST.getlist('degree_subject')
    ):
        # This will raise a 500 error page on production
        return render(request, '500.html', {'term': settings.TERM})
    # Once input is seemingly valid render the view:
    academic_year = AcademicYear.objects.get(year=settings.ACADEMIC_YEAR)
    # Save POST parameters to cookie:
    if request.method == 'POST':
        request.session['degree_subject'] = request.POST.getlist('degree_subject')
    # degree_subjects contains a list with strings with the format
    # {subject_id}_{group}
    raw_selected_subjects = request.session['degree_subject']
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
            'calendar_name': calendar.name,
        }
        return render(request, 'calendar.html', context)


def subscription(request):
    # First, deal with invalid inputs:
    if (
        request.method == 'GET' or
        not request.POST["email"] or
        not request.POST["password"] or
        not request.POST["calendar"]
    ):
        # This will render a 500 error page on production
        return render(request, '500.html', {'term': settings.TERM})
    # Once input is seemingly valid render the view:
    email = request.POST["email"]
    password = request.POST["password"]
    calendar = request.POST["calendar"]
    result = subprocess.call(
        [settings.PHANTOMJS_BIN, settings.AUTO_SUBSCRIPTION_SCRIPT, email, password, calendar])
    return render(request, 'subscription_result.html', {'result': result})


def contact(request):
    if request.method == 'POST':  # If the form has been submitted...
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = '[HP] [SUPORT] {}'.format(form.cleaned_data['subject'])
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']
            recipients = ['horarispompeu@gmail.com']

            from django.core.mail import send_mail
            send_mail(subject, message, sender, recipients)
            return HttpResponseRedirect('/gracies/')
    else:
        form = ContactForm()

    return render(request, 'contact.html', {
        'form': form,
    })
