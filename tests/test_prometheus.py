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

from zyxelprometheus import prometheus

XDSL = open("example_xdsl.txt").read()
IFCONFIG = open("example_ifconfig.txt").read()


class TestPrometheus(unittest.TestCase):
    def test_values(self):
        prom = prometheus(XDSL, IFCONFIG)

        self.assertIn("""zyxel_line_rate{bearer=0,stream="up"} 7833000""",
                      prom)
        self.assertIn("""zyxel_packets{stream="tx",iface="ppp2.3"}"""
                      + """ 7334759""", prom)
