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

from zyxelprometheus.server import Handler, Scraper

from .mock_sshclient import MockSSHClient, MockSSHSession

XDSL = open("example_xdsl.txt").read()
IFCONFIG = open("example_ifconfig.txt").read()


class MockHandler(Handler):
    def __init__(self):
        self.wfile = io.BytesIO()
        self.requestline = "GET"
        self.client_address = ("127.0.0.1", 8000)
        self.request_version = "1.0"
        self.command = "GET"


class TestServer(unittest.TestCase):
    def setUp(self):
        MockSSHClient.reset()

        session = MockSSHSession()
        session.add_cmd("ifconfig\n", IFCONFIG)
        session.add_cmd("xdslctl info\n", XDSL)
        MockSSHClient.add_session("192.168.1.1",
                                  "testuser",
                                  "testpassword",
                                  session)

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

    def test_metrics(self):
        class Args:
            host = "192.168.1.1"
            user = "testuser"
            passwd = "testpassword"
            traffic_only = False
            xdsl_only = False

        MockHandler.scraper = Scraper(Args())

        handler = MockHandler()
        handler.path = "/metrics"
        handler.do_GET()

        handler.wfile.seek(0)
        self.assertTrue(
            "zyxel_line_rate" in handler.wfile.read().decode("utf8"))
