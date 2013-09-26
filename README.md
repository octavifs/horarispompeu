# Horaris Pompeu

Horaris Pompeu is a Django webapp that makes it easy to create custom calendars adapted to each students' needs. Calendars can be subscribed using Google Calendar, and synchronized on any computer or mobile device.

Calendar creation is a one-time process. Subscribed calendars refresh automatically, so they always stay up to date with the ones published in the ESUP webpage.

## Features
- parses subjects and lessons from ESUP timetable to its own DB schema
- handles subject aliases and inconsistencies in the timetables
- able to manually add, delete or modify erroneous entries
- detects and processes inserted or deleted lessons in the official timetables
- able to automatically update generated calendars to stay up to date with the official timetables
- web interface optimized for mobile and desktop

## Documentation

See the [docs overview](docs/overview.md).

## Dependencies
See [requirements.txt](requirements.txt).

## Supported degrees and faculties
3 degrees (given by the ESUP) are supported:

- Grau en Enginyeria de Sistemes Audiovisuals
- Grau en Enginyeria de Telemàtica
- Grau en Enginyeria en Informàtica

The database schema should be flexible enough so that adding new degrees and faculties is an easy task.


## Usage
    WARNING. Somewhat out of date

1. Put the timetable folder inside your django project.
2. Update the `settings.py` of your django project to include `timetable` in the `INSTALLED_APPS` variable.
3. `python manage.py syncdb` to prepare the database.
4. `python manage.py initdb` to insert some initial data (regarding degrees, years, etc.
5. `python manage.py subjectparser` to retrieve the list of available subjects by the ESUP. This list may need to be revised by hand. Go to the admin page (or `dbshell`) and delete any Subject duplicate.
6. `python manage.py aliasparser`. Then you will have to assign any subject aliases without Subject to a Subject entry. This step is necessary because the data source is not consistent. It has mispellings and abreviations for the same subject, that may or may not appear.
7. `python manage.py lessonparser`. This should insert all the lessons into the database. It should be noted that it stores the HTML it uses to extract the information into the directory indicated by the sources/esup.py file, so you will want to change that.
8. Change any `MEDIA_URL` or `STATIC_URL` from the `settings.py` to adjust it to your needs.
9. Execute `python manage.py lessonparser` periodically so the Lessons and Calendars are kept up to date.


## License
This software is released under the Apache 2 License. See LICENSE for more details.