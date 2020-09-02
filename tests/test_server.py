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

import io
import json
from datetime import datetime, timedelta
import unittest

import responses

from zyxelprometheus.server import Handler, Scraper

from .test_login import RESPONSE as LOGIN_RESPONSE

XDSL = open("example_xdsl.txt").read()
TRAFFIC = open("example_traffic.json").read()

TRAFFIC_URL = "https://192.168.1.1/cgi-bin/DAL?oid=Traffic_Status"
XDSL_URL = "https://192.168.1.1/cgi-bin/xDSLStatistics_handle?line=0"


class MockHandler(Handler):
    def __init__(self):
        self.wfile = io.BytesIO()
        self.requestline = "GET"
        self.client_address = ("127.0.0.1", 8000)
        self.request_version = "1.0"
        self.command = "GET"


class TestServer(unittest.TestCase):
    def test_index(self):
        handler = MockHandler()
        handler.path = "/"
        handler.do_GET()

        handler.wfile.seek(0)
        self.assertTrue("/metrics" in handler.wfile.read().decode("utf8"))

    def test_error(self):
        handler = MockHandler()
        handler.path = "/error"
        handler.do_GET()

        handler.wfile.seek(0)
        self.assertTrue("404" in handler.wfile.read().decode("utf8"))

    @responses.activate
    def test_metrics(self):
        responses.add(responses.POST, "https://192.168.1.1/UserLogin",
                      body=LOGIN_RESPONSE,
                      status=200)
        responses.add(responses.GET, XDSL_URL,
                      status=200, body=json.dumps([{"result": XDSL}]))
        responses.add(responses.GET, TRAFFIC_URL,
                      status=200, body=TRAFFIC)

        class Args:
            host = "https://192.168.1.1"
            user = "testuser"
            passwd = "testpasswd"
            traffic_only = False
            xdsl_only = False

        MockHandler.scraper = Scraper(Args())

        handler = MockHandler()
        handler.path = "/metrics"
        handler.do_GET()

        handler.wfile.seek(0)
        self.assertTrue(
            "zyxel_line_rate" in handler.wfile.read().decode("utf8"))

    @responses.activate
    def test_relogin(self):
        login_response = json.loads(LOGIN_RESPONSE)
        login_response["sessionkey"] = 1234
        login_response2 = json.dumps(login_response)

        responses.add(responses.POST, "https://192.168.1.1/UserLogin",
                      body=LOGIN_RESPONSE,
                      status=200)
        responses.add(responses.POST, "https://192.168.1.1/UserLogin",
                      body=login_response2,
                      status=200)
        responses.add(responses.POST, "https://192.168.1.1/cgi-bin/UserLogout?"
                      + "sessionkey=816284860",
                      status=200)
        responses.add(responses.GET, XDSL_URL,
                      status=200, body=json.dumps([{"result": XDSL}]))
        responses.add(responses.GET, TRAFFIC_URL,
                      status=200, body=TRAFFIC)

        class Args:
            host = "https://192.168.1.1"
            user = "testuser"
            passwd = "testpasswd"
            traffic_only = False
            xdsl_only = False

        MockHandler.scraper = Scraper(Args())

        handler = MockHandler()
        handler.path = "/metrics"
        handler.do_GET()

        MockHandler.scraper.login_time = \
            datetime.utcnow() - timedelta(minutes=45)

        handler = MockHandler()
        handler.path = "/metrics"
        handler.do_GET()

        self.assertEquals(1234, MockHandler.scraper.sessionkey)
