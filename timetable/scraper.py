from datetime import datetime
import asyncio
import aiohttp
import contextlib
from time import mktime

from bs4 import BeautifulSoup
from django.conf import settings
from timetable.models import AcademicYear, Faculty, Degree, DegreeSubject,\
    Subject, Lesson


# Defines max number of concurrent connections employed by the scraper module
MAX_CONNECTIONS = 20
# Defines a semaphore which allows for a total of MAX_CONNECTIONS concurrent acquires
SEMAPHORE = asyncio.Semaphore(MAX_CONNECTIONS)


class Node(object):
    """
    Lesson tree:
    +- planDocente (1:N)
    `+- centro (1:N)
     `+- estudio (1:1)
      `+- planEstudio (1:N)
       `+- curso (1:3)
        `+- trimestre (1:2)
         `+- grupo (1:N)
          `+- asignaturas
    """
    def __init__(self, name=None, keys=None, data=None):
        self.name = name or ''
        self.keys = keys or {}
        self.data = data or {}

    def __str__(self):
        return '<Node {}>\nkeys: {}\ndata: {}'.format(
            self.name,
            repr(self.keys),
            repr(self.data)
        )

@asyncio.coroutine
def setup_session_id(s):
    """
    Makes the request that will create the unique id necessary for GestioAcademica
    API to work properly
    """
    r = yield from s.get(
        'https://gestioacademica.upf.edu/pds/consultaPublica/' +
        'look%5bconpub%5dInicioPubHora?entradaPublica=true&idiomaPais=ca.ES'
    )
    yield from r.release()

@asyncio.coroutine
def update_html(plan_docente=None, centro=None, estudio=None, plan_estudio=None,
                curso=None, trimestre=None, grupo=None):
    data = {
        'planDocente': plan_docente,
        'centro': centro,
        'estudio': estudio,
        'planEstudio': plan_estudio,
        'curso': curso,
        'trimestre': trimestre,
        'grupo': grupo,
        'idPestana': 1
    }
    data = {key: val for key, val in data.items() if val}
    with (yield from SEMAPHORE):
        with aiohttp.ClientSession(connector=aiohttp.TCPConnector()) as s:
            yield from setup_session_id(s)
            r = yield from s.post(
                'https://gestioacademica.upf.edu/pds/consultaPublica/' +
                'look[conpub]ActualizarCombosPubHora', data=data)
            d = yield from r.read()
            return BeautifulSoup(d)

@asyncio.coroutine
def parse_plan_docente(html, *args):
    options = html.form.find('select', id='planDocente').find_all('option')
    options = {
        entry.attrs['value']: entry.text for entry in options
    }
    nodes = yield from asyncio.gather(*(parse(*args, plan_docente=key) for key in options))
    return Node(
        name='planDocente',
        keys=options,
        data={key: node for key, node in zip(options, nodes)}
    )


@asyncio.coroutine
def parse_centro(html, *args):
    options = html.form.find('select', id='centro').find_all('option')
    options = {
        entry.attrs['value']: entry.text for entry in options
        if entry.attrs['value'] != '-1'
    }
    nodes = yield from asyncio.gather(*(parse(*args, centro=key) for key in options))
    return Node(
        name='centro',
        keys=options,
        data={key: node for key, node in zip(options, nodes)}
    )


@asyncio.coroutine
def parse_estudio(html, *args):
    options = html.form.find('select', id='estudio').find_all('option')
    options = {
        entry.attrs['value']: entry.text for entry in options
        if entry.attrs['value'] != '-1'
    }
    nodes = yield from asyncio.gather(*(parse(*args, estudio=key) for key in options))
    return Node(
        name='estudio',
        keys=options,
        data={key: node for key, node in zip(options, nodes)}
    )


@asyncio.coroutine
def parse_plan_estudio(html, *args):
    """planEstudio is a 1:1 relation with studio, but we simulate 1:N with a
    list of 1
    """
    options = [html.form.find('input', id='planEstudio')]
    options = {
        entry.attrs['value']: entry.text for entry in options
        if entry.attrs['value'] != '-1'
    }
    nodes = yield from asyncio.gather(*(parse(*args, plan_estudio=key) for key in options))
    return Node(
        name='planEstudio',
        keys=options,
        data={key: nodes for key, nodes in zip(options, nodes)}
    )


@asyncio.coroutine
def parse_curso(html, *args):
    """-1 is used as Optatives in this case, so it's useful"""
    options = html.form.find('select', id='curso').find_all('option')
    options = {
        entry.attrs['value']: entry.text for entry in options
    }
    nodes = yield from asyncio.gather(*(parse(*args, curso=key) for key in options))
    return Node(
        name='curso',
        keys=options,
        data={key: nodes for key, nodes in zip(options, nodes)}
    )


@asyncio.coroutine
def parse_trimestre(html, *args):
    options = html.form.find('select', id='trimestre').find_all('option')
    options = {
        entry.attrs['value']: entry.text for entry in options
    }
    nodes = yield from asyncio.gather(*(parse(*args, trimestre=key) for key in options))
    return Node(
        name='trimestre',
        keys=options,
        data={key: nodes for key, nodes in zip(options, nodes)}
    )


@asyncio.coroutine
def parse_grupo(html, *args):
    options = html.form.find('select', id='grupo').find_all('option')
    options = {
        entry.attrs['value']: entry.text for entry in options
        if entry.attrs['value'] != '-1'
    }
    nodes = yield from asyncio.gather(*(parse(*args, grupo=key) for key in options))
    return Node(
        name='grupo',
        keys=options,
        data={key: nodes for key, nodes in zip(options, nodes)}
    )


@asyncio.coroutine
def parse_subjects(html, *args):
    options = html.form.find('select', id='asignaturas').find_all('option')
    options = {
        entry.attrs['value']: entry.text for entry in options
    }
    return Node(
        name='asignaturas',
        keys=options,
        data={key: None for key in options}
    )


@asyncio.coroutine
def parse(plan_docente=None, centro=None, estudio=None, plan_estudio=None,
          curso=None, trimestre=None, grupo=None):
    try:
        html = yield from update_html(plan_docente, centro, estudio, plan_estudio, curso,
                           trimestre, grupo)
        if grupo:
            result = yield from parse_subjects(html, plan_docente, centro, estudio,
                                  plan_estudio, curso, trimestre, grupo)
        elif trimestre:
            result = yield from parse_grupo(html, plan_docente, centro, estudio,
                               plan_estudio, curso, trimestre)
        elif curso:
            result = yield from parse_trimestre(html, plan_docente, centro, estudio,
                                   plan_estudio, curso)
        elif plan_estudio:
            result = yield from parse_curso(html, plan_docente, centro, estudio,
                               plan_estudio)
        elif estudio:
            result = yield from parse_plan_estudio(html, plan_docente, centro, estudio)
        elif centro:
            result = yield from parse_estudio(html, plan_docente, centro)
        elif plan_docente:
            result = yield from parse_centro(html, plan_docente)
        else:
            result = yield from parse_plan_docente(html)
        return result
    except AttributeError:
        # This may be triggered if we are trying to parse something the form
        # does not have Such as subjects for a faculty, or stuff like that
        return None


def flatten_tree(node, max_depth='asignaturas', data=None):
    """
    Returns an iterator with the dicts necessary to retrieve all possible
    timetables of all UPF. Ain't that rad?
    """
    data = data or {
        'planDocente': None,
        'centro': None,
        'estudio': None,
        'planEstudio': None,
        'curso': None,
        'trimestre': None,
        'grupo': None,
        'asignaturas': None
    }
    # Empty children ends recursion
    if not node:
        return
    # Reaching max_depth node yields dict
    if node.name == max_depth:
        for key, val in node.keys.items():
            copy = dict(data)
            copy[node.name] = (key, val)
            yield copy
        return
    # Recursion
    for key, val in node.keys.items():
        data[node.name] = (key, val)
        for entry in flatten_tree(node.data[key], max_depth, dict(data)):
            yield entry

def populate_db():
    loop = asyncio.get_event_loop()
    root = loop.run_until_complete(parse())
    # Process academic years
    for entry in flatten_tree(root, 'planDocente'):
        course_key, course = entry['planDocente']
        AcademicYear.objects.get_or_create(year=course, year_key=course_key)
    # Process Faculties
    for entry in flatten_tree(root, 'centro'):
        name_key, name = entry['centro']
        Faculty.objects.get_or_create(name=name, name_key=name_key)
    # Process Degrees
    for entry in flatten_tree(root, 'planEstudio'):
        faculty = Faculty.objects.get(name=entry['centro'][1])
        name_key, name = entry['estudio']
        plan_key = entry['planEstudio'][0]
        Degree.objects.get_or_create(name=name,
                                     name_key=name_key,
                                     plan_key=plan_key,
                                     faculty=faculty)
    # Process Subjects & DegreeSubjects
    for entry in flatten_tree(root, 'asignaturas'):
        faculty = Faculty.objects.get(name=entry['centro'][1])
        name_key, name = entry['estudio']
        plan_key = entry['planEstudio'][0]
        degree, created = Degree.objects.get_or_create(
            name=name,
            name_key=name_key,
            plan_key=plan_key,
            faculty=faculty)
        name_key, name = entry['asignaturas']
        subject, created = Subject.objects.get_or_create(degree=degree,
                                                         name=name,
                                                         name_key=name_key)
        academic_year = AcademicYear.objects.get(year=entry['planDocente'][1])
        course_key, course = entry['curso']
        term_key, term = entry['trimestre']
        group_key, group = entry['grupo']
        DegreeSubject.objects.get_or_create(subject=subject,
                                            degree=degree,
                                            academic_year=academic_year,
                                            course=course,
                                            course_key=course_key,
                                            term=term,
                                            term_key=term_key,
                                            group=group,
                                            group_key=group_key)


def populate_lessons(degree_subjects):
    """
    Given an iterable of degree_subjects, get the related lessons and upsert
    them into the DB.
    """

    @asyncio.coroutine
    def store_ds_lessons(ds):
        data = {
            'planDocente': ds.academic_year.year_key,
            'centro': ds.degree.faculty.name_key,
            'estudio': ds.degree.name_key,
            'planEstudio': ds.degree.plan_key,
            'curso': ds.course_key,
            'trimestre': ds.term_key,
            'grupo': ds.group_key,
            'asignaturas': ds.subject.name_key,
            'asignatura' + ds.subject.name_key: ds.subject.name_key
        }
        with (yield from SEMAPHORE):
            with aiohttp.ClientSession(connector=aiohttp.TCPConnector()) as s:
                yield from setup_session_id(s)
                r = yield from s.post('https://gestioacademica.upf.edu/pds/consultaPublica/'
                                        'look[conpub]MostrarPubHora', data=data)
                yield from r.read()
                # Date range is from 1st september to 1st of july. It covers the whole academic year so
                # 1 request per subject is enough
                today = datetime.now()
                curr_academic_year = today.year if today.month < 9 else today.year + 1
                start_time = int(mktime(datetime(curr_academic_year - 1, 9, 1).timetuple()))
                end_time = int(mktime(datetime(curr_academic_year, 7, 1).timetuple()))
                lessons = yield from s.get(
                    'https://gestioacademica.upf.edu/pds/consultaPublica/[Ajax]selecionarRangoHorarios'
                    '?start=%d&end=%d' % (start_time, end_time)
                )
                raw_lessons = yield from lessons.json()
        # Delete previously stored lessons related to that degreesubject
        # this way we make sure we only keep the latest data
        Lesson.objects.filter(
            subject=ds.subject,
            group_key=ds.group_key,
            academic_year=ds.academic_year,
            term=ds.term).delete()
        for raw_lesson in raw_lessons:
            if raw_lesson['festivoNoLectivo']:
                continue
            Lesson(
                subject=ds.subject,
                group_key=ds.group_key,
                date_start=datetime.strptime(raw_lesson["start"],
                                             "%Y-%m-%d %H:%M:%S"),
                date_end=datetime.strptime(raw_lesson["end"],
                                           "%Y-%m-%d %H:%M:%S"),
                academic_year=ds.academic_year,
                term=ds.term,
                entry="\n".join((raw_lesson["tipologia"], raw_lesson["grup"])),
                location=raw_lesson["aula"]).save()

    # populate_lessons logic starts now
    tasks = asyncio.wait([store_ds_lessons(ds) for ds in degree_subjects])
    loop = asyncio.get_event_loop()
    loop.run_until_complete(tasks)

