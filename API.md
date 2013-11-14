# API DOCS

## Summary

This is very much work in progress. Might be inaccurate. The relevant source code
is [/timetable/urls_api.py][endpoints] and [/timetable/api.py][implementation].
None of the API methods require any sort of authentication and, right now, none
of them can perform any writes on the DB. Right now, the API is read-only.

[endpoints]: https://github.com/octavifs/horarispompeu/blob/rest_api/timetable/urls_api.py
[implementation]: https://github.com/octavifs/horarispompeu/blob/rest_api/timetable/api.py


## Endpoint

[http://www.horarispompeu.com/api](http://www.horarispompeu.com/api)


## Methods

### GET /faculties

Returns all the faculties stored in the DB. Right now, this is only the ESUP.

### GET /faculties/{id}

Returns faculty with id {id}.

### GET /degrees

Lists all degrees. This is basically CS, Telecommunications and Audiovisuals.

Can filter results by name:

    http://www.horarispompeu.com/api/degrees?name=Audiovisuals
    [
      {
        "pk": 1, 
        "model": "timetable.degree", 
        "fields": {
          "name": "Grau en Enginyeria de Sistemes Audiovisuals", 
          "faculty": "ESUP"
        }
      }
    ]

### GET /degrees/{id}

Return degree with id {id}.

### GET /subjects

Lists all subjects. Subjects are linked to a faculty, but not to any degree in particular.

Can be filtered by name, same as degrees.

### GET /subjects/{id}

Returns subject with id {id}.

### GET /courses

Lists all courses. A course is a subject taught in a specific academic year, degree and group:

    {
      pk: 294
      model: "timetable.degreesubject"
      fields: {
        academic_year: "2013-14"
        group: "GRUP 1"
        degree: 2
        term: "1r Trimestre"
        year: "1r"
        subject: 82
      }
    }

Can be filtered by subject, degree, year, term or group, in a similar fashion to
the previous queries. Subject or degree, in this filtering, has to referr to the PK
of the object. For example, if we want to know which Càlcul i Mètodes Numérics courses
are being taught, first we have to know the PK of the subject, so we do:

    http://www.horarispompeu.com/api/subjects?name=Càlcul
    [
      {
        "pk": 82, 
        "model": "timetable.subject", 
        "fields": {
          "name": "Càlcul i Mètodes Numèrics", 
          "faculty": "ESUP"
        }
      }
    ]

Once we have the PK of the subject, we can ask for its courses:

    http://www.horarispompeu.com/api/courses?subject=82
    [
      {
        "pk": 249, 
        "model": "timetable.degreesubject", 
        "fields": {
          "academic_year": "2013-14", 
          "group": "GRUP 1", 
          "degree": 1, 
          "term": "1r Trimestre", 
          "year": "1r", 
          "subject": 82
        }
      }, 
      {
        "pk": 294, 
        "model": "timetable.degreesubject", 
        "fields": {
          "academic_year": "2013-14", 
          "group": "GRUP 1", 
          "degree": 2, 
          "term": "1r Trimestre", 
          "year": "1r", 
          "subject": 82
        }
      }, 
      ...
    ]

### GET /courses/{id}

Returns course with id {id}.

### GET /courses/{id}/lessons

Returns all the lessons linked to a specific course:

    https://www.horarispompeu.com/api/courses/249/lessons
    [
      {
        "pk": 5295, 
        "model": "timetable.lesson", 
        "fields": {
          "kind": "SEMINARI", 
          "group": "GRUP 1", 
          "room": "52.105", 
          "date_end": "2013-09-27T11:30:00", 
          "date_start": "2013-09-27T10:30:00", 
          "academic_year": "2013-14", 
          "raw_entry": "Càlcul i Mètodes Numèrics\r\n\nSEMINARI\n\r\n10:30 - 11:30\r\n\r\nS101: 52.105\r\n\r\nS103: 52.329\r\n\r\nS105: 52.321\r\n\r\n11:30 - 12:30\r\n\r\nS102: 52.105\r\n\r\nS104: 52.329\r\n\r\nS106: 52.321", 
          "subgroup": "S101", 
          "subject": 82
        }
      }, 
      {
        "pk": 5300, 
        "model": "timetable.lesson", 
        "fields": {
          "kind": "SEMINARI", 
          "group": "GRUP 1", 
          "room": "52.105", 
          "date_end": "2013-09-27T12:30:00", 
          "date_start": "2013-09-27T11:30:00", 
          "academic_year": "2013-14", 
          "raw_entry": "Càlcul i Mètodes Numèrics\r\n\nSEMINARI\n\r\n10:30 - 11:30\r\n\r\nS101: 52.105\r\n\r\nS103: 52.329\r\n\r\nS105: 52.321\r\n\r\n11:30 - 12:30\r\n\r\nS102: 52.105\r\n\r\nS104: 52.329\r\n\r\nS106: 52.321", 
          "subgroup": "S102", 
          "subject": 82
        }
      }, 
      ...
    ]

