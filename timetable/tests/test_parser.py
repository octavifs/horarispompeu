# encoding: utf-8

from __future__ import unicode_literals
from django.test import TestCase
from datetime import time, date, datetime
from bs4 import BeautifulSoup
from timetable.management.commands import _parser as parser


class LessonTests(TestCase):
    """
    Tests suite for the Lesson object
    """
    def setUp(self):
        self.lesson = parser.Lesson(
            raw_data="Dummy raw data",
            subject="Boring class",
            group="S101"
        )

        self.setA = set([
            parser.Lesson(
                raw_data="Dummy raw data",
                subject="Boring class",
                group="S101"
            ),
            parser.Lesson(
                raw_data="Dummy raw data 2",
                subject="Boring class 2",
                group="S102"
            ),
            parser.Lesson(
                raw_data="Dummy raw data",
                subject="Boring class",
                group="S103"
            ),
        ])

        self.setB = set([
            parser.Lesson(
                raw_data="Dummy raw data",
                subject="Boring class",
                kind="TEORIA",
                room="52.119"
            ),
            parser.Lesson(
                raw_data="Dummy raw data 2",
                subject="Boring class 2",
                group="S102"
            ),
            parser.Lesson(
                raw_data="Dummy raw data",
                subject="Boring class",
                group="S103"
            ),
        ])

    def test_constructor(self):
        lesson_repr = "<Lesson object>\n" \
            "subject: u'Boring class'\n" \
            "kind: None\n" \
            "group: u'S101'\n" \
            "room: None\n" \
            "date_start: None\n" \
            "date_end: None\n" \
            "raw_data: u'Dummy raw data'"
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

    def test_set_intersection(self):
        intersection = set([
            parser.Lesson(
                raw_data="Dummy raw data 2",
                subject="Boring class 2",
                group="S102"
            ),
            parser.Lesson(
                raw_data="Dummy raw data",
                subject="Boring class",
                group="S103"
            ),
        ])
        # Elements common in both sets
        self.assertEqual(self.setA & self.setB, intersection)

    def test_set_union(self):
        union = set([
            parser.Lesson(
                raw_data="Dummy raw data",
                subject="Boring class",
                group="S101"
            ),
            parser.Lesson(
                raw_data="Dummy raw data 2",
                subject="Boring class 2",
                group="S102"
            ),
            parser.Lesson(
                raw_data="Dummy raw data",
                subject="Boring class",
                group="S103"
            ),
            parser.Lesson(
                raw_data="Dummy raw data",
                subject="Boring class",
                kind="TEORIA",
                room="52.119"
            ),
        ])
        # Combined unique elements of setA and setB
        self.assertEqual(self.setA | self.setB, union)

    def test_set_difference(self):
        differenceA = set([
            parser.Lesson(
                raw_data="Dummy raw data",
                subject="Boring class",
                group="S101"
            ),
        ])
        differenceB = set([
            parser.Lesson(
                raw_data="Dummy raw data",
                subject="Boring class",
                kind="TEORIA",
                room="52.119"
            ),
        ])
        # Elements in A not found in B
        self.assertEqual(self.setA - self.setB, differenceA)
        # Elements in B not found in A
        self.assertEqual(self.setB - self.setA, differenceB)
        # Elements not common in both sets
        self.assertEqual(self.setA ^ self.setB, differenceA | differenceB)


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


class ParserTests(TestCase):
    """
    Test suite for the parser functions
    """
    def test_parsehours(self):
        data = [
            "12:30-14:30",
            "12:30 - 13:30",
            "10:30 - 11:30",
            "11.00 a 13.00 h",
        ]
        results = [
            (time(12, 30), time(14, 30)),
            (time(12, 30), time(13, 30)),
            (time(10, 30), time(11, 30)),
            (time(11, 00), time(13, 00)),
        ]
        for d, r in zip(data, results):
            result = parser.parsehours(d)
            self.assertEqual(result, r)

    def test_parsedays(self):
        data = """
            <tr bgcolor="#cccc99">
                <td nowrap="nowrap">
                    <div align="center"><strong>Hora</strong></div>
                </td>
                <td>
                    <div align="center"><strong>11/11/2013</strong></div>
                </td>
                <td>
                    <div align="center"><strong>12/11/2013</strong></div>
                </td>
                <td>
                    <div align="center"><strong>13/11/2013</strong></div>
                </td>
                <td>
                    <div align="center"><strong>14/11/2013</strong></div>
                </td>
                <td>
                    <div align="center"><strong>15/11/2013</strong></div>
                </td>
            </tr>
        """
        results = [
            None,
            date(2013, 11, 11),
            date(2013, 11, 12),
            date(2013, 11, 13),
            date(2013, 11, 14),
            date(2013, 11, 15),
        ]
        parsed_data = BeautifulSoup(data)
        response = parser.parsedays(parsed_data)
        for e, r in zip(response, results):
            self.assertEqual(e, r)

    def test_parselesson(self):
        data = [
            (
                (
                    "Càlcul i Mètodes Numèrics\nNO HI HA CLASSE",
                    time(8, 30),
                    time(10, 30),
                    date(2013, 11, 11)
                ),
                ()
            ),
            (
                (
                    "Introducció a les TIC \nSEMINARI \nS204: 52.429 \nS205: 52.329 \nS206: 52.105 \nS202: 52.323",
                    time(8, 30),
                    time(10, 30),
                    date(2013, 11, 11)
                ),
                (
                    parser.Lesson(
                        subject="Introducció a les TIC",
                        kind="SEMINARI",
                        group="S204",
                        room="52.429",
                    ),
                    parser.Lesson(
                        subject="Introducció a les TIC",
                        kind="SEMINARI",
                        group="S205",
                        room="52.329",
                    ),
                    parser.Lesson(
                        subject="Introducció a les TIC",
                        kind="SEMINARI",
                        group="S206",
                        room="52.105",
                    ),
                    parser.Lesson(
                        subject="Introducció a les TIC",
                        kind="SEMINARI",
                        group="S202",
                        room="52.323",
                    )
                )
            ),
            (
                (
                    "Principis de Telecomunicació \nTEORIA \nAula: 52.119 ",
                    time(8, 30),
                    time(10, 30),
                    date(2013, 11, 14)
                ),
                (
                    parser.Lesson(
                        subject="Principis de Telecomunicació",
                        kind="TEORIA",
                        group=None,
                        room="52.119",
                    ),
                )
            ),
            (
                (
                    "Càlcul i Mètodes Numèrics \nTEORIA \nT2A: 52.019 \nT2B: 52.223",
                    time(8, 30),
                    time(10, 30),
                    date(2013, 11, 11)
                ),
                (
                    parser.Lesson(
                        subject="Càlcul i Mètodes Numèrics",
                        kind="TEORIA",
                        group="T2A",
                        room="52.019",
                    ),
                    parser.Lesson(
                        subject="Càlcul i Mètodes Numèrics",
                        kind="TEORIA",
                        group="T2B",
                        room="52.223",
                    ),
                )
            ),
            (
                (
                    "Xarxes i Serveis \nTEORIA \nAula: 52.019 + 52.123\n",
                    time(8, 30),
                    time(10, 30),
                    date(2013, 11, 11)
                ),
                (
                    parser.Lesson(
                        subject="Xarxes i Serveis",
                        kind="TEORIA",
                        group=None,
                        room="52.019 + 52.123",
                    ),
                )
            ),
            (
                (
                    "\nCàlcul i Mètodes Numèrics \nSEMINARI \n10:30 - 11:30 \nS201: 52.105 \nS203: 52.429 \nS205: 52.221 \n11:30 - 12:30 \nS202: 52.105 \nS204: 52.429 \nS206: 52.221 \n",
                    time(8, 30),
                    time(10, 30),
                    date(2013, 11, 11)
                ),
                (
                    parser.Lesson(
                        subject="Càlcul i Mètodes Numèrics",
                        kind="SEMINARI",
                        group="S201",
                        room="52.105",
                        date_start=datetime(2013, 11, 11, 10, 30),
                        date_end=datetime(2013, 11, 11, 11, 30),
                    ),
                    parser.Lesson(
                        subject="Càlcul i Mètodes Numèrics",
                        kind="SEMINARI",
                        group="S203",
                        room="52.429",
                        date_start=datetime(2013, 11, 11, 10, 30),
                        date_end=datetime(2013, 11, 11, 11, 30),
                    ),
                    parser.Lesson(
                        subject="Càlcul i Mètodes Numèrics",
                        kind="SEMINARI",
                        group="S205",
                        room="52.221",
                        date_start=datetime(2013, 11, 11, 10, 30),
                        date_end=datetime(2013, 11, 11, 11, 30),
                    ),
                    parser.Lesson(
                        subject="Càlcul i Mètodes Numèrics",
                        kind="SEMINARI",
                        group="S202",
                        room="52.105",
                        date_start=datetime(2013, 11, 11, 11, 30),
                        date_end=datetime(2013, 11, 11, 12, 30),
                    ),
                    parser.Lesson(
                        subject="Càlcul i Mètodes Numèrics",
                        kind="SEMINARI",
                        group="S204",
                        room="52.429",
                        date_start=datetime(2013, 11, 11, 11, 30),
                        date_end=datetime(2013, 11, 11, 12, 30),
                    ),
                    parser.Lesson(
                        subject="Càlcul i Mètodes Numèrics",
                        kind="SEMINARI",
                        group="S206",
                        room="52.221",
                        date_start=datetime(2013, 11, 11, 11, 30),
                        date_end=datetime(2013, 11, 11, 12, 30),
                    ),
                )
            ),
            (
                (
                    "\nAplicacions Intel·ligents per a la Web \nPRÀCTIQUES \nP102: 54.004 \n--------------------------------------- \nRàdiocomunicacions \nNO HI HA CLASSE \n--------------------------------------- \nRobòtica \nNO HI HA CLASSE\n",
                    time(8, 30),
                    time(10, 30),
                    date(2013, 11, 11)
                ),
                (
                    parser.Lesson(
                        subject="Aplicacions Intel·ligents per a la Web",
                        kind="PRÀCTIQUES",
                        group="P102",
                        room="54.004",
                    ),
                )
            ),
            (
                (
                    "\nAplicacions Intel·ligents per a la Web \nSEMINARI \nS101: 54.004 \n--------------------------------------- \nRàdiocomunicacions \nSEMINARI \nS101: 54.028 \n--------------------------------------- \nRobòtica \nTEORIA \nAula: 52.223 \n",
                    time(8, 30),
                    time(10, 30),
                    date(2013, 11, 11)
                ),
                (
                    parser.Lesson(
                        subject="Aplicacions Intel·ligents per a la Web",
                        kind="SEMINARI",
                        group="S101",
                        room="54.004",
                    ),
                    parser.Lesson(
                        subject="Ràdiocomunicacions",
                        kind="SEMINARI",
                        group="S101",
                        room="54.028",
                    ),
                    parser.Lesson(
                        subject="Robòtica",
                        kind="TEORIA",
                        group=None,
                        room="52.223",
                    ),
                )
            ),
        ]
        # Copy the raw data to each lesson
        for d, r in data:
            for l in r:
                l.raw_data = d[0].strip()
                l.date_start = datetime.combine(d[3], d[1]) if not l.date_start else l.date_start
                l.date_end = datetime.combine(d[3], d[2]) if not l.date_end else l.date_end
        for d, r in data:
            response = tuple(parser.parselesson(*d))
            for e1, e2 in zip(response, r):
                self.assertEqual(e1, e2)

    def test_parse(self):
        data = """
        <table id="taula_11" border="1" cellpadding="0" cellspacing="0" style="width: 99%;font-family: Helvetica, Verdana, Arial, sans-serif;">
        <tbody><tr bgcolor="#cccc99">
        <td nowrap="nowrap" width="10%">
        <div align="center"><strong>Setmana 11</strong></div>
        </td>
        <td width="18%">
        <div align="center"><strong>DILLUNS</strong></div>
        </td>
        <td width="18%">
        <div align="center"><strong>DIMARTS</strong></div>
        </td>
        <td width="18%">
        <div align="center"><strong>DIMECRES</strong></div>
        </td>
        <td width="18%">
        <div align="center"><strong>DIJOUS</strong></div>
        </td>
        <td width="18%">
        <div align="center"><strong>DIVENDRES</strong></div>
        </td>
        </tr>
        <tr bgcolor="#cccc99">
        <td nowrap="nowrap">
        <div align="center"><strong>Hora</strong></div>
        </td>
        <td>
        <div align="center"><strong>02/12/2013</strong></div>
        </td>
        <td>
        <div align="center"><strong>03/12/2013</strong></div>
        </td>
        <td>
        <div align="center"><strong>04/12/2013</strong></div>
        </td>
        <td>
        <div align="center"><strong>05/12/2013</strong></div>
        </td>
        <td>
        <div align="center"><strong>06/12/2013</strong></div>
        </td>
        </tr>
        <tr bgcolor="#ffcc99">
        <td nowrap="nowrap">
        <div align="center"><strong>08:30-10:30</strong></div>
        </td>
        <td id="cela_87">
        <div align="center">
        Polítiques Públiques de TIC
        <br>
        <b>PRÀCTIQUES</b>
        <br>
        Aula: 52.119
        <br>
        </div>
        </td>
        <td id="cela_88">
        <div align="center">
        Aplicacions Intel·ligents per a la Web
        <br>
        <b>PRÀCTIQUES</b>
        <br>
        P101: 54.004
        <br>
        ---------------------------------------
        <br>
        Ràdiocomunicacions
        <br>
        NO HI HA CLASSE
        <br>
        ---------------------------------------
        <br>
        Robòtica
        <br>
        <b>PRÀCTIQUES</b>
        <br>
        P101: 54.003
        <br>
        </div>
        </td>
        <td>
        <div align="center">
        <br>
        </div></td>
        <td bgcolor="#cccc99">
        <div align="center">
        <br><b>FESTIU</b><br><br>
        </div></td>
        <td bgcolor="#cccc99">
        <div align="center">
        <br><b>FESTIU</b><br><br>
        </div></td>
        </tr>
        <tr bgcolor="#ffcc99">
        <td nowrap="nowrap">
        <div align="center"><strong>10:30-12:30</strong></div>
        </td>
        <td>
        <div align="center">
        <br>
        </div></td>
        <td>
        <div align="center">
        <br>
        </div></td>
        <td>
        <div align="center">
        <br>
        </div></td>
        <td bgcolor="#cccc99">
        <div align="center">
        <br><b>FESTIU</b><br><br>
        </div></td>
        <td bgcolor="#cccc99">
        <div align="center">
        <br><b>FESTIU</b><br><br>
        </div></td>
        </tr>
        <tr bgcolor="#ffcc99">
        <td nowrap="nowrap">
        <div align="center"><strong>12:30-14:30</strong></div>
        </td>
        <td>
        <div align="center">
        <br>
        </div></td>
        <td id="cela_89">
        <div align="center">
        Polítiques Públiques de TIC
        <br>
        NO HI HA CLASSE
        <br>
        </div>
        </td>
        <td id="cela_90">
        <div align="center">
        Aplicacions Intel·ligents per a la Web
        <br>
        <b>PRÀCTIQUES</b>
        <br>
        P102: 54.004
        <br>
        ---------------------------------------
        <br>
        Ràdiocomunicacions
        <br>
        NO HI HA CLASSE
        <br>
        ---------------------------------------
        <br>
        Robòtica
        <br>
        NO HI HA CLASSE
        <br>
        </div>
        </td>
        <td bgcolor="#cccc99">
        <div align="center">
        <br><b>FESTIU</b><br><br>
        </div></td>
        <td bgcolor="#cccc99">
        <div align="center">
        <br><b>FESTIU</b><br><br>
        </div></td>
        </tr>
        <tr bgcolor="#ffcc99">
        <td nowrap="nowrap">
        <div align="center"><strong>14:30-16:30</strong></div>
        </td>
        <td>
        <div align="center">
        <br>
        </div></td>
        <td id="cela_91">
        <div align="center">
        Fonaments Computacionals dels SAV
        <br>
        NO HI HA CLASSE
        <br>
        ---------------------------------------
        <br>
        Projectes Basats en Software Lliure
        <br>
        <b>PRÀCTIQUES</b>
        <br>
        P101: 54.005
        <br>
        </div>
        </td>
        <td>
        <div align="center">
        <br>
        </div></td>
        <td bgcolor="#cccc99">
        <div align="center">
        <br><b>FESTIU</b><br><br>
        </div></td>
        <td bgcolor="#cccc99">
        <div align="center">
        <br><b>FESTIU</b><br><br>
        </div></td>
        </tr>
        <tr bgcolor="#ffcc99">
        <td nowrap="nowrap">
        <div align="center"><strong>16:30-18:30</strong></div>
        </td>
        <td>
        <div align="center">
        <br>
        </div></td>
        <td>
        <div align="center">
        <br>
        </div></td>
        <td>
        <div align="center">
        <br>
        </div></td>
        <td bgcolor="#cccc99">
        <div align="center">
        <br><b>FESTIU</b><br><br>
        </div></td>
        <td bgcolor="#cccc99">
        <div align="center">
        <br><b>FESTIU</b><br><br>
        </div></td>
        </tr>
        <tr bgcolor="#ffcc99">
        <td nowrap="nowrap">
        <div align="center"><strong>18:30-20:30</strong></div>
        </td>
        <td>
        <div align="center">
        <br>
        </div></td>
        <td>
        <div align="center">
        <br>
        </div></td>
        <td id="cela_92">
        <div align="center">
        Fonaments Computacionals dels SAV
        <br>
        NO HI HA CLASSE
        <br>
        ---------------------------------------
        <br>
        Projectes Basats en Software Lliure
        <br>
        <b>PRÀCTIQUES</b>
        <br>
        P101: 54.003
        <br>
        </div>
        </td>
        <td bgcolor="#cccc99">
        <div align="center">
        <br><b>FESTIU</b><br><br>
        </div></td>
        <td bgcolor="#cccc99">
        <div align="center">
        <br><b>FESTIU</b><br><br>
        </div></td>
        </tr>
        </tbody>
        </table>
        """
        results = (
            parser.Lesson(
                subject="Polítiques Públiques de TIC",
                kind="PRÀCTIQUES",
                room="52.119",
                date_start=datetime(2013, 12, 2, 8, 30),
                date_end=datetime(2013, 12, 2, 10, 30),
            ),
            parser.Lesson(
                subject="Aplicacions Intel·ligents per a la Web",
                kind="PRÀCTIQUES",
                group="P101",
                room="54.004",
                date_start=datetime(2013, 12, 3, 8, 30),
                date_end=datetime(2013, 12, 3, 10, 30),
            ),
            parser.Lesson(
                subject="Robòtica",
                kind="PRÀCTIQUES",
                group="P101",
                room="54.003",
                date_start=datetime(2013, 12, 3, 8, 30),
                date_end=datetime(2013, 12, 3, 10, 30),
            ),
            parser.Lesson(
                subject="Aplicacions Intel·ligents per a la Web",
                kind="PRÀCTIQUES",
                group="P102",
                room="54.004",
                date_start=datetime(2013, 12, 4, 12, 30),
                date_end=datetime(2013, 12, 4, 14, 30),
            ),
            parser.Lesson(
                subject="Projectes Basats en Software Lliure",
                kind="PRÀCTIQUES",
                group="P101",
                room="54.005",
                date_start=datetime(2013, 12, 3, 14, 30),
                date_end=datetime(2013, 12, 3, 16, 30),
            ),
            parser.Lesson(
                subject="Projectes Basats en Software Lliure",
                kind="PRÀCTIQUES",
                group="P101",
                room="54.003",
                date_start=datetime(2013, 12, 4, 18, 30),
                date_end=datetime(2013, 12, 4, 20, 30),
            ),
        )
        response = tuple(parser.parse(data))
        for r1, r2 in zip(response, results):
            r2.raw_data = r1.raw_data
            self.assertEqual(r1, r2)
