# Horaris Pompeu

Horaris Pompeu is a Django webapp that makes it easy to create custom calendars adapted to each students. Calendars can be subscribed using Google Calendar, and synchronized on any computer or mobile device.

Calendar creation is a one-time process. Subscribed calendars refresh automatically, so they always stay up to date with the ones published in the ESUP webpage.


## Features
- parses subjects and lessons from ESUP timetable to its own DB schema
- handles subject aliases and inconsistencies in the timetables
- able to manually add, delete or modify erroneous entries
- detects and processes inserted or deleted lessons in the official timetables
- able to automatically update generated calendars to stay up to date with the official timetables
- web interface optimized for mobile and desktop
- automated backups

## Supported degrees and faculties
3 degrees (given by the ESUP) are supported:

- Grau en Enginyeria de Sistemes Audiovisuals
- Grau en Enginyeria de Telemàtica
- Grau en Enginyeria en Informàtica

If new parsers are implemented, it should be possible to add new degrees and faculties with ease.


## Dependencies
horarispompeu requires **python 2.7**. Python packages are listed in the [requirements.txt](requirements.txt) file, and can be installed via pip.

Horarispompeu uses nginx for static content and as a reverse proxy and supervisord to ensure it keeps running, but both are optional.


## Installation
First, install via apt:
    
    sudo apt-get install nginx supervisor python2.7 python2.7-pip

Once that is taken care of, set up virtualenv (skip if you already have):
    
    sudo pip install virtualenv virtualenvwrapper

Add to the .bashrc (skip if you already have):

    export WORKON_HOME=$HOME/.virtualenvs
    source /usr/local/bin/virtualenvwrapper.sh

Create a virtualenv (you might need to reenter the terminal so .bashrc changes can take effect):

    mkvirtualenv horarispompeu

Clone the repo and install requirements:
    workon horarispompeu
    git clone https://github.com/octavifs/horarispompeu
    pip install -r requirements.txt

Install phantomJS (version 1.9.2 used. Later versions may work):
    
    cd /to/wherever/you/want/to/download/the/source
    wget https://phantomjs.googlecode.com/files/phantomjs-1.9.2-linux-x86_64.tar.bz2
    tar -xvf phantomjs-1.9.2-linux-x86_64.tar.bz2
    cd phantomjs-1.9.2-linux-x86_64/
    sudo ln -sf `pwd`/bin/phantomjs /usr/local/bin/phantomjs

You may want to set up nginx and supervisor. A sample config is provided in the repo. I would recommend to setup nginx with a SSL cert (HTTPS server) if you plan on using the automated login functionality.

To set up the django app, first of all create a `settings_private.py` file alongside `settings.py`, with the correct config for the parameters specified in the `settings.py` file.

Once that is completed:

    ./manage.py syncdb
    ./manage.py collectstatic

And this should be it. The service should be able to run via `./manage.py runserver` or gunicorn, uwsgi or whatever WSGI server of your choosing.


## Workflows

### Change term or academic year
1. Modify the TERM or ACADEMIC_YEAR variables under `settings.py`
2. Erase DegreeSubjects table (`echo 'DELETE FROM timetable_faculty;' | ./manage.py dbshell`)
3. `./manage.py subjectparser`. Make sure you take care of any empty aliases via admin interface.
4. `./manage.py lessonparser`

### Add new static content
    ./manage.py collectstatic

If new static content is added or modified (be it images, CSS, javascript) run:


### Parse timetables for subjects
    ./manage.py subjectparser

This is the first command to run. Make sure that it completes successfully and that every alias has a valid subject linked to it. Aliases are necessary since the same subject can be written in different ways accross the timetable.


### Parse timetables for lessons
    ./manage.py lessonparser

This parses the timetables, compares them with the previous downloaded version, and adds / deletes any change that has been performed.


### Update all created calendars
    ./manage.py calendarupdater

Updates all the .ics files created with the latest version of the lessons, as parsed by lessonparser.


### Update all, backup, send mail to admin
    ./manage.py updater

Executes all of the above commands, backs up the DB, config and timetables and sends an e-mail to the admin, so it's easy to check whether the process has been completed successfully or not. It's convenient to have this command added as a cron task.

My crontab:
    
    @daily /home/horaris/horarispompeu/updater.sh

*updater.sh*:
    
    #!/bin/bash
    # Virtualenvwrapper configuration
    export WORKON_HOME=$HOME/.virtualenvs
    source /usr/local/bin/virtualenvwrapper.sh
    cd /home/horaris/horarispompeu
    workon horarispompeu
    ./manage.py updater

### Check latest added lesson in the admin panel
Open the Lessons view in the django admin and sort by creation date. The admin interface allows all sorts of sorting and filtering: by date, subject, start, end, type of lesson, etc.

### SubjectAlias an Subject
The SubjectAlias model always has to be linked with a Subject. Sometimes, the correct Subject for the SubjectAlias simply does not exist. In this case, a new Subject can be created directly from the detail view in the SubjectAlias admin panel.

### Creating a subjects.json file
The `subjects.json` file has been created via `./manage.py subjectstojson` and then manually curated (the automatic output has some repeated entries, etc.). It should not change from year to year, so it's pretty safe to leave it alone. In any case, any subject in subjects.json will be added to the DB whenever *subjectparser* is run.

### Adding new timetables
`timetables.json` holds all the information related to where the timetables are to be found (URL) and to which degree, academic year and group they refer to. To add new timetables, just append them to the timetables.json or create a new one following the same format.


## License
This software is released under the Apache 2 License. See LICENSE for more details.
