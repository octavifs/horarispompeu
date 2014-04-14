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
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.core.files.base import ContentFile
from django.views.generic import ListView, FormView, TemplateView
from django.http import Http404

from django.conf import settings

from timetable.models import *
import timetable.calendar
from timetable.forms import ContactForm


class FacultyList(ListView):
    template_name = 'faculty.html'
    model = Faculty

    def get_queryset(self):
        faculties = (d.faculty.id for d in Degree.objects.all())
        queryset = super(FacultyList, self).get_queryset()
        return queryset.filter(id__in=faculties)


class DegreeList(ListView):
    template_name = 'degree.html'
    model = Degree
    allow_empty = False

    def get_queryset(self):
        queryset = super(DegreeList, self).get_queryset()
        faculties = self.request.GET.getlist("faculty")
        return queryset.filter(faculty__in=faculties)


class CourseList(TemplateView):
    template_name = 'course.html'
    http_method_names = 'get'

    def get_context_data(self, **kwargs):
        queryset = DegreeSubject.objects.all()
        degrees = self.request.GET.getlist("degree")
        degree_and_group_list = queryset.filter(
            degree__in=degrees,
            academic_year=settings.ACADEMIC_YEAR,
        ).order_by(
            'degree',
            'course_key',
            'group'
        ).values(
            'degree',
            'degree__name',
            'course',
            'course_key',
            'group',
            'group_key'
        ).distinct()
        if not degree_and_group_list:
            raise Http404
        degree_list = {}
        for entry in degree_and_group_list:
            degree_list.setdefault(entry['degree__name'], []).append(entry)
        return {'degree_list': degree_list}


class SubjectView(TemplateView):
    template_name = 'subject.html'
    http_method_names = 'get'

    def get_context_data(self, **kwargs):
        degree_course = self.request.GET.getlist('degree_course')
        if not degree_course:
            raise Http404
        courses = []
        for entry in degree_course:
            degree_id, course_key, group_key = entry.split('_')
            courses.append((degree_id, course_key, group_key))
        q_list = []
        for degree, course, group in courses:
            q = Q(degree=degree, course_key=course, group_key=group,
                  academic_year=settings.ACADEMIC_YEAR)
            q_list.append(q)
        degree_subjects = DegreeSubject.objects.filter(
            reduce(operator.or_, q_list)
        ).order_by(
            'course',
            'subject__name',
        ).values(
            'degree',
            'degree__name',
            'subject',
            'subject__name',
            'group',
            'group_key',
            'course',
            'course_key',
        ).distinct()
        degree_course_subjects = {}
        for ds in degree_subjects:
            degree_course_subjects[ds['degree__name']] = {}
        for ds in degree_subjects:
            degree_course_subjects[ds['degree__name']][ds['group']] = []
        for ds in degree_subjects:
            degree_course_subjects[ds['degree__name']][ds['group']].append(ds)
        print degree_course_subjects
        return {
            'degree_course_subjects': degree_course_subjects
        }


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


class ContactView(FormView):
    form_class = ContactForm
    success_url = reverse_lazy('thanks')
    template_name = 'contact.html'

    def form_valid(self, form):
        subject = '[HP] [SUPORT] {}'.format(form.cleaned_data['subject'])
        message = form.cleaned_data['message']
        sender = form.cleaned_data['sender']
        recipients = ['horarispompeu@gmail.com']
        from django.core.mail import send_mail
        send_mail(subject, message, sender, recipients)

        return super(ContactView, self).form_valid(form)
