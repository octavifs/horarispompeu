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

## License
This software is released under the Apache 2 License. See LICENSE for more details.