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

import json
import unittest

from zyxelprometheus import login, scrape_ifconfig, scrape_xdsl

from .mock_sshclient import MockSSHClient, MockSSHSession

IFCONFIG = open("example_ifconfig.txt").read()
XDSL = open("example_xdsl.txt").read()


class TestScrape(unittest.TestCase):
    def setUp(self):
        MockSSHClient.reset()

        session = MockSSHSession()
        session.add_cmd("ifconfig\n", IFCONFIG)
        session.add_cmd("xdslctl info\n", XDSL)
        MockSSHClient.add_session("192.168.1.1",
                                  "admin",
                                  "testpassword",
                                  session)

    def test_scrape_ifconfig(self):
        session = login("192.168.1.1",
                        "admin",
                        "testpassword")

        ifconfig = scrape_ifconfig(session)

        self.assertTrue("192.168.1.1" in ifconfig)

    def test_scrape_xdsl(self):
        session = login("192.168.1.1",
                        "admin",
                        "testpassword")

        xdsl = scrape_xdsl(session)

        self.assertTrue("Status: Showtime" in xdsl)
