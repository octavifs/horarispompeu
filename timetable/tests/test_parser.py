from django.test import TestCase
from timetable.management.commands import _parser as parser


class LessonTests(TestCase):
    """
    Tests suite for the Lesson object
    """
    def setUp(self):
        self.lesson = parser.Lesson()
        self.lesson.raw_data = "Dummy raw data"
        self.lesson.group = "S101"
        self.lesson.subject = "Boring class"

    def test_constructor(self):
        lesson_repr = "<Lesson object>\n" \
            "subject: 'Boring class'\n" \
            "kind: None\n" \
            "group: 'S101'\n" \
            "room: None\n" \
            "date_start: None\n" \
            "date_end: None\n" \
            "raw_data: 'Dummy raw data'"
        self.assertEqual(repr(self.lesson), lesson_repr)

    def test_equality(self):
        lesson_cpy = self.lesson.copy()
        # First test that the objects are 2 different instances:
        self.assertIsNot(self.lesson, lesson_cpy)
        # Then test that the 2 objects are equal
        self.assertEqual(self.lesson, lesson_cpy)

    def test_inequality(self):
        lesson_cpy = self.lesson.copy()
        lesson_cpy.subject = "Cool class"
        self.assertNotEqual(self.lesson, lesson_cpy)


class RegexpTests(TestCase):
    """
    Tests to demonstrate which strings can be parsed by the regular expressions
    and which can't.
    """
    def test_regexp_date(self):
        matches = [
            "12:30-14:30",
            "12:30 - 13:30",
            "10:30 - 11:30",
            "11.00 a 13.00 h",
        ]
        groups = [
            ("12", "30", "14", "30"),
            ("12", "30", "13", "30"),
            ("10", "30", "11", "30"),
            ("11", "00", "13", "00"),
        ]
        for m, group in zip(matches, groups):
            match = parser.regexp_date.match(m)
            self.assertIsNotNone(match, msg=m + "does not match!")
            self.assertEqual(match.groups(), group)

        not_matches = [
            "S101: 52.321",
        ]
        for m in not_matches:
            match = parser.regexp_date.match(m)
            self.assertIsNone(match, msg=m + "does match!")

    def test_regexp_room(self):
        matches = [
            "Aula: 52.019 + 52.023",
            "T2A: 52.019",
            "T2B: 52.221",
            "P101: 54.004",
            "S103: 52.221",
            "S104:52.329",
            "Aules: 52.019, 52.121, 52.221 i 52.223",
            "P103: 52.221+ 52.217",
            "S206: 52.329",
        ]
        groups = [
            ("52.019 + 52.023",),
            ("52.019",),
            ("52.221",),
            ("54.004",),
            ("52.221",),
            ("52.329",),
            ("52.019, 52.121, 52.221 i 52.223",),
            ("52.221+ 52.217",),
            ("52.329",),
        ]
        for m, group in zip(matches, groups):
            match = parser.regexp_room.match(m)
            self.assertIsNotNone(match, msg=m + "does not match!")
            self.assertEqual(match.groups(), group)

        not_matches = [
            "S101 i S102: 52.329",
            "S103 i S104: 52.019",
        ]
        for m in not_matches:
            match = parser.regexp_room.match(m)
            self.assertIsNone(match)

    def test_regexp_group(self):
        matches = [
            "T2A: 52.019",
            "T2B: 52.221",
            "P101: 54.004",
            "S103: 52.221",
            "S104:52.329",
            "P103: 52.221+ 52.217",
            "S206: 52.329",
        ]
        groups = [
            ("T2A",),
            ("T2B",),
            ("P101",),
            ("S103",),
            ("S104",),
            ("P103",),
            ("S206",),
        ]
        for m, group in zip(matches, groups):
            match = parser.regexp_group.match(m)
            self.assertIsNotNone(match, msg=m + "does not match!")
            self.assertEqual(match.groups(), group)

        not_matches = [
            "Aula: 52.019 + 52.023",
            "Aules: 52.019, 52.121, 52.221 i 52.223",
            "S101 i S102: 52.329",
            "S103 i S104: 52.019",
        ]
        for m in not_matches:
            match = parser.regexp_group.match(m)
            self.assertIsNone(match)
