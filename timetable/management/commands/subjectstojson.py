#encoding: utf-8

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

"""
Django command utility. Parses HTML and returns JSON file with a list of
subjects by faculty.
"""
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
import requests
from bs4 import BeautifulSoup
import io
import sys
from collections import defaultdict
import json

SUBJECTS = {
    "ESUP": [
        "http://www.upf.edu/pra/3377/",  # Informàtica
        "http://www.upf.edu/pra/3376/",  # Telemàtica
        "http://www.upf.edu/pra/3375/",  # Audiovisuals
    ],
}


def parse_url_to_subjects(url):
    # Get HTML source
    html_source = requests.get(url).text
    # Parse HTML
    html_parsed = BeautifulSoup(html_source)
    # Get all subjects from html source
    # Subject names are inside <li> tags with the class 'sumari'
    # Like this:
    # <li class="sumari">
    #   <a href="/pra/3376/21293.pdf" title="&nbsp;21293">21293</a>
    #   &nbsp;Introducció a les TIC
    # </li>
    subjects = []
    for entry in html_parsed.find_all(name='li', attrs={'class': 'sumari'}):
        subject_name = entry.text[6:]
        subjects.append(subject_name)
    # Return subjects
    return subjects


class Command(BaseCommand):
    help = """Parse subjects from faculties and save them into a JSON file.
If no output file is defined, output is written to stdout.

Usage:
./manage.py subjectstojson
./manage.py subjectstojson output_file
"""
    args = "out_file_path"

    def handle(self, *args, **options):
        try:
            # Write to file if specified by arguments. If not, write to stdout
            if not args:
                output_file = sys.stdout
            else:
                output_file = io.open(args[0], "w", encoding="utf-8")
            faculty_subjects = defaultdict(set)
            # Parse all subjects and put them into a list
            for faculty, urls in SUBJECTS.iteritems():
                for url in urls:
                    subjects = parse_url_to_subjects(url)
                    faculty_subjects[faculty].update(subjects)
            # This middle step is necessary since set() is not JSON serializable
            for faculty, subjects in faculty_subjects.iteritems():
                faculty_subjects[faculty] = tuple(subjects)
            # Convert dict to JSON
            # Options make sure the return value is not converted to ascii (it
            # remains a unicode object), the keys are sorted and the file is
            # properly indented
            json_out = json.dumps(faculty_subjects, sort_keys=True, indent=4,
                                  ensure_ascii=False)
            # Write result to file descriptor
            output_file.write(json_out)
            output_file.write('\n')
        finally:
            output_file.close()
