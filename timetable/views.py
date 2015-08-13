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



import operator
import hashlib
import subprocess

from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy, reverse
from django.db.models import Q
from django.core.files.base import ContentFile
from django.views.generic import TemplateView, FormView, View
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404

from django.conf import settings

from timetable.models import *
from timetable import ical
from timetable.forms import ContactForm
from functools import reduce


# TemplateView will also have a dispatch handler for POST requests
# (same function as GET)
# See the source for dispatch:
# https://github.com/django/django/blob/master/django/views/generic/base.py#L79
# TemplateView only defines a get handler by default
TemplateView.post = TemplateView.get


class FacultyList(TemplateView):
    template_name = 'faculty.html'

    def get_context_data(self, **kwargs):
        faculties = (d.faculty.id for d in Degree.objects.all())
        return {'faculty_list': Faculty.objects.filter(id__in=faculties)}


class DegreeList(TemplateView):
    template_name = 'degree.html'

    def get_context_data(self, **kwargs):
        faculties = (self.request.REQUEST.getlist("faculty") or
                     self.request.session.get("faculty"))
        if not faculties:
            raise Http404
        self.request.session["faculty"] = faculties
        queryset = Degree.objects.filter(faculty__in=faculties)
        return {'degree_list': queryset}


class CourseList(TemplateView):
    template_name = 'course.html'

    def get_context_data(self, **kwargs):
        queryset = DegreeSubject.objects.all()
        degrees = (self.request.REQUEST.getlist("degree") or
                   self.request.session.get("degree"))
        if not degrees:
            raise Http404
        self.request.session["degree"] = degrees
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
        degree_list = {}
        for entry in degree_and_group_list:
            degree_list.setdefault(entry['degree__name'], []).append(entry)
        return {'degree_list': degree_list}


class SubjectView(TemplateView):
    template_name = 'subject.html'

    def get_context_data(self, **kwargs):
        degree_course = (self.request.REQUEST.getlist('degree_course') or
                         self.request.session.get('degree_course'))
        if not degree_course:
            raise Http404
        # Store in cookies
        self.request.session['degree_course'] = degree_course
        courses = []
        for entry in degree_course:
            degree_id, course_key, group_key = entry.split('_')
            courses.append((degree_id, course_key, group_key))
        degree_subjects = DegreeSubject.objects.none()
        for degree, course, group in courses:
            degree_subjects = degree_subjects | DegreeSubject.objects.filter(
                degree=degree,
                course_key=course,
                group_key=group,
                academic_year=settings.ACADEMIC_YEAR,
                term_key=settings.TERM
            )
        degree_subjects = degree_subjects.order_by(
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
            'course_key'
        ).distinct()
        degree_course_subjects = {}
        for ds in degree_subjects:
            degree_course_subjects[ds['degree__name']] = {}
        for ds in degree_subjects:
            degree_course_subjects[ds['degree__name']][ds['course']] = []
        for ds in degree_subjects:
            ids = "_".join(str(ds.id) for ds in DegreeSubject.objects.filter(
                degree=ds['degree'],
                subject=ds['subject'],
                group_key=ds['group_key'],
                course_key=ds['course_key']))
            ds["ids"] = ids
            degree_course_subjects[ds['degree__name']][ds['course']].append(ds)
        return {
            'degree_course_subjects': degree_course_subjects
        }


class CalendarView(TemplateView):
    template_name = 'calendar.html'

    def get_context_data(self, **kwargs):
        degree_subject = (self.request.REQUEST.getlist("degree_subject") or
                          self.request.session.get("degree_subject"))
        if not degree_subject:
            raise Http404
        self.request.session["degree_subject"] = degree_subject
        # Now, get a clear list of required degree_subjects
        degree_subject_ids = set()
        for ds in degree_subject:
            for id in ds.split("_"):
                degree_subject_ids.add(int(id))
        #DegreeSubjects Hash
        degree_subjects_str = " ".join(str(id)
                                       for id in sorted(degree_subject_ids))
        degree_subjects_hash = hashlib.sha1(degree_subjects_str.encode("utf8")).hexdigest()
        calendar = None
        try:
            calendar = Calendar.objects.get(name=degree_subjects_hash)
        except Calendar.DoesNotExist:
            degree_subjects = DegreeSubject.objects.filter(
                id__in=degree_subject_ids)
            calendar = Calendar(name=degree_subjects_hash, )
            calendar.save()
            calendar.degree_subjects.add(*degree_subjects)
        finally:
            return {
                'calendar_url': self.request.build_absolute_uri(
                    reverse('icalendar', kwargs={'pk': calendar.name})),
                'calendar_name': calendar.name,
            }


class ICalendarView(View):
    def get(self, request, *args, **kwargs):
        calendar = get_object_or_404(Calendar, name=self.kwargs['pk'])
        q_list = []
        for ds in calendar.degree_subjects.all():
            q = Q(
                subject=ds.subject,
                group_key=ds.group_key,
                academic_year=settings.ACADEMIC_YEAR)
            q_list.append(q)
        lessons_filter = reduce(operator.or_, q_list)
        lessons = Lesson.objects.filter(lessons_filter)
        response = HttpResponse(ical.generate(lessons))
        response['Content-Type'] = 'text/calendar;charset=utf-8'
        return response


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
        [settings.PHANTOMJS_BIN, settings.AUTO_SUBSCRIPTION_SCRIPT, email,
         password, calendar])
    return render(request, 'subscription_result.html', {'result': result})


class ContactView(FormView):
    form_class = ContactForm
    success_url = reverse_lazy('thanks')
    template_name = 'contact.html'

    def form_valid(self, form):
        subject = '[HP] [SUPORT] {}'.format(form.cleaned_data['subject'])
        message = form.cleaned_data['message']
        sender = form.cleaned_data['sender']
        recipients = [settings.SUPPORT_EMAIL]
        from django.core.mail import send_mail
        send_mail(subject, message, sender, recipients)

        return super(ContactView, self).form_valid(form)
