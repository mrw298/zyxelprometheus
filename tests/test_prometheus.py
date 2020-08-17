# zyxelprometheus
# Copyright (C) 2020 Andrew Wilkinson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from base64 import b64decode
import json
import unittest

import responses

from zyxelprometheus import prometheus

XDSL = open("example_xdsl.txt").read()
TRAFFIC = json.load(open("example_traffic.json"))


class TestPrometheus(unittest.TestCase):
    @responses.activate
    def test_values(self):
        prom = prometheus(XDSL, TRAFFIC)

        self.assertIn("""zyxel_line_rate{stream="up"} 7386169""", prom)
        self.assertIn("""zyxel_packets{stream="up",iface="wan"}"""
                      + """ 1201548572""", prom)
