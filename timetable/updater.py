# encoding: utf-8
from __future__ import unicode_literals
import hashlib
import timetable.management.commands._parser as parser


def is_html_equal(old_html, new_html):
    """
    Check if 2 strings (containing the html document with a timetable) are equal
    """
    return hash(old_html) == hash(new_html)


def substracted_lessons(old_html, new_html):
    lessons_old = set(parser.parse(old_html))
    lessons_new = set(parser.parse(new_html))
    return lessons_old - lessons_new


def added_lessons(old_html, new_html):
    lessons_old = set(parser.parse(old_html))
    lessons_new = set(parser.parse(new_html))
    return lessons_new - lessons_old
