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

import responses

from zyxelprometheus import login, scrape_xdsl, scrape_traffic

from .test_login import RESPONSE as LOGIN_RESPONSE

XDSL = open("example_xdsl.txt").read()
TRAFFIC = open("example_traffic.json").read()

TRAFFIC_URL = "https://192.168.1.1/cgi-bin/DAL?oid=Traffic_Status"
XDSL_URL = "https://192.168.1.1/cgi-bin/xDSLStatistics_handle?line=0"


class TestScrape(unittest.TestCase):
    @responses.activate
    def test_scrape_xdsl(self):
        responses.add(responses.POST, "https://192.168.1.1/UserLogin",
                      body=LOGIN_RESPONSE,
                      status=200)
        responses.add(responses.GET, XDSL_URL,
                      status=200, body=json.dumps([{"result": XDSL}]))

        session, sessionkey = login("https://192.168.1.1",
                                    "admin",
                                    "testpassword")

        xdsl = scrape_xdsl(session, "https://192.168.1.1")

        self.assertTrue("VDSL Training Status" in xdsl)

    @responses.activate
    def test_scrape_traffic(self):
        responses.add(responses.POST, "https://192.168.1.1/UserLogin",
                      body=LOGIN_RESPONSE,
                      status=200)
        responses.add(responses.GET, TRAFFIC_URL,
                      status=200, body=TRAFFIC)

        session, sessionkey = login("https://192.168.1.1",
                                    "admin",
                                    "testpassword")

        traffic = scrape_traffic(session, "https://192.168.1.1")

        self.assertEquals("ZCFG_SUCCESS", traffic["result"])
