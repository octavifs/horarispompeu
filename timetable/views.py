from __future__ import unicode_literals
from django.http import HttpResponse
from django.template import Context, loader

from timetable.models import Subject


# Create your views here.
def index(request):
    subject_list = Subject.objects.all()
    template = loader.get_template('index.html')
    context = Context({
        'subject_list': subject_list
    })
    return HttpResponse(template.render(context))
