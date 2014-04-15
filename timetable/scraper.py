import re
from datetime import datetime

from bs4 import BeautifulSoup
import requests
from timetable.models import AcademicYear, Faculty, Degree, DegreeSubject,\
    Subject, Lesson


# Create a global session for the script, that will hold the necessary cookies
# to perform valid HTTP requests to the backend
SESSION = requests.Session()


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


def update_html(plan_docente=None, centro=None, estudio=None, plan_estudio=None,
                curso=None, trimestre=None, grupo=None):
    data = {
        'planDocente': plan_docente,
        'centro': centro,
        'estudio': estudio,
        'planEstudio': plan_estudio,
        'curso': curso,
        'trimestre': trimestre,
        'grupo': grupo
    }
    r = SESSION.post(
        'http://gestioacademica.upf.edu/pds/consultaPublica/' +
        'look[conpub]ActualizarCombosPubHora', data=data)
    return BeautifulSoup(r.text)


def parse_plan_docente(html, *args):
    options = html.form.find('select', id='planDocente').find_all('option')
    options = {
        entry.attrs['value']: entry.text for entry in options
    }
    return Node(
        name='planDocente',
        keys=options,
        data={key: parse(*args, plan_docente=key) for key in options}
    )


def parse_centro(html, *args):
    options = html.form.find('select', id='centro').find_all('option')
    options = {
        entry.attrs['value']: entry.text for entry in options
        if entry.attrs['value'] != '-1'
    }
    return Node(
        name='centro',
        keys=options,
        data={key: parse(*args, centro=key) for key in options}
    )


def parse_estudio(html, *args):
    options = html.form.find('select', id='estudio').find_all('option')
    options = {
        entry.attrs['value']: entry.text for entry in options
        if entry.attrs['value'] != '-1'
    }
    return Node(
        name='estudio',
        keys=options,
        data={key: parse(*args, estudio=key) for key in options}
    )


def parse_plan_estudio(html, *args):
    """planEstudio is a 1:1 relation with studio, but we simulate 1:N with a
    list of 1
    """
    options = [html.form.find('input', id='planEstudio')]
    options = {
        entry.attrs['value']: entry.text for entry in options
        if entry.attrs['value'] != '-1'
    }
    return Node(
        name='planEstudio',
        keys=options,
        data={key: parse(*args, plan_estudio=key) for key in options}
    )


def parse_curso(html, *args):
    """-1 is used as Optatives in this case, so it's useful"""
    options = html.form.find('select', id='curso').find_all('option')
    options = {
        entry.attrs['value']: entry.text for entry in options
    }
    return Node(
        name='curso',
        keys=options,
        data={key: parse(*args, curso=key) for key in options}
    )


def parse_trimestre(html, *args):
    options = html.form.find('select', id='trimestre').find_all('option')
    options = {
        entry.attrs['value']: entry.text for entry in options
    }
    return Node(
        name='trimestre',
        keys=options,
        data={key: parse(*args, trimestre=key) for key in options}
    )


def parse_grupo(html, *args):
    options = html.form.find('select', id='grupo').find_all('option')
    options = {
        entry.attrs['value']: entry.text for entry in options
        if entry.attrs['value'] != '-1'
    }
    return Node(
        name='grupo',
        keys=options,
        data={key: parse(*args, grupo=key) for key in options}
    )


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


def parse(plan_docente=None, centro=None, estudio=None, plan_estudio=None,
          curso=None, trimestre=None, grupo=None):
    try:
        html = update_html(plan_docente, centro, estudio, plan_estudio, curso,
                           trimestre, grupo)
        if grupo:
            return parse_subjects(html, plan_docente, centro, estudio,
                                  plan_estudio, curso, trimestre, grupo)
        elif trimestre:
            return parse_grupo(html, plan_docente, centro, estudio,
                               plan_estudio, curso, trimestre)
        elif curso:
            return parse_trimestre(html, plan_docente, centro, estudio,
                                   plan_estudio, curso)
        elif plan_estudio:
            return parse_curso(html, plan_docente, centro, estudio,
                               plan_estudio)
        elif estudio:
            return parse_plan_estudio(html, plan_docente, centro, estudio)
        elif centro:
            return parse_estudio(html, plan_docente, centro)
        elif plan_docente:
            return parse_centro(html, plan_docente)
        else:
            return parse_plan_docente(html)
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
        for key, val in node.keys.iteritems():
            copy = dict(data)
            copy[node.name] = (key, val)
            yield copy
        return
    # Recursion
    for key, val in node.keys.iteritems():
        data[node.name] = (key, val)
        for entry in flatten_tree(node.data[key], max_depth, dict(data)):
            yield entry


def init_session():
    # Set up session cookies
    global SESSION
    SESSION = requests.Session()
    SESSION.get(
        'http://gestioacademica.upf.edu/pds/consultaPublica/' +
        'look%5bconpub%5dInicioPubHora?entradaPublica=true&idiomaPais=ca.ES'
    )


def populate_db():
    # Set up session cookies
    init_session()
    # Parse entire tree
    root = parse()
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
    # Set up session cookies
    init_session()
    # Compile regex
    # This regex matches a JS Object found in the retrieved HTML
    lesson_re = re.compile(r"""
        \{\ s*
        title:\s*\"(?P<title>.*)\",\s*
        aula:\s*\"(?P<aula>.*)\",\s*
        tipologia:\s*\"(?P<tipologia>.*)\",\s*
        grup:\s*\"(?P<grup>.*)\",\s*
        start:\s*\"(?P<start>.*)\",\s*
        end:\s*\"(?P<end>.*)\",\s*
        className:\s*\"(?P<className>.*)\",\s*
        festivoNoLectivo:\s*(?P<festivoNoLectivo>true|false),\s*
        publicarObservacion:\s*\"(?P<publicarObservacion>.*)\",\s*
        observacion:\s*\"(?P<observacion>.*)\"\s*
        \}""", re.VERBOSE)

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
        r = SESSION.post('http://gestioacademica.upf.edu/pds/consultaPublica/'
                         'look[conpub]MostrarPubHora', data=data)
        raw_lessons = (m.groupdict() for m in lesson_re.finditer(r.text))
        if raw_lessons:
            # Delete previously stored lessons related to that degreesubject
            # this way we make sure we only keep the latest data
            Lesson.objects.filter(
                subject=ds.subject,
                group_key=ds.group_key,
                academic_year=ds.academic_year,
                term=ds.term).delete()
        for raw_lesson in raw_lessons:
            if raw_lesson['festivoNoLectivo'] == 'true':
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

    for ds in degree_subjects:
        store_ds_lessons(ds)
