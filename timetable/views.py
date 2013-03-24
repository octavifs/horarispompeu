from __future__ import unicode_literals
from django.http import HttpResponse
from django.template import Context, loader

from timetable.models import Class


# Create your views here.
def index(request):
    classes_list = Class.objects.all()
    template = loader.get_template('index.html')
    context = Context({
        'classes_list': classes_list
    })
    return HttpResponse(template.render(context))
