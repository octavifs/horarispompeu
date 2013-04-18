# Horaris Pompeu

Horaris pompeu is a Django app that enables students from the University Pompeu Fabra (Barcelona) to create their own timetables by selecting any combination subjects and creating a custom iCalendar (.ics) file that can be subscribed from Google Calendar and synchronized from any computer or mobile device.

The Django app also updates the calendars with new events automatically, so you will never be caught off guard.


## Supported degrees and faculties
3 degrees (given by the ESUP) are supported:

- Grau en Enginyeria de Sistemes Audiovisuals
- Grau en Enginyeria de Telemàtica
- Grau en Enginyeria en Informàtica

The database schema should be flexible enough so that adding new degrees and faculties is an easy task.


## Usage
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