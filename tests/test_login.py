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
from unittest.mock import patch

from zyxelprometheus import login, logout, InvalidPassword

from .mock_sshclient import MockSSHClient, MockSSHSession

RESPONSE = json.dumps({
    "sessionkey": 816284860,
    "ThemeColor": "",
    "changePw": False,
    "showSkipBtn": False,
    "quickStart": False,
    "loginAccount": "admin",
    "loginLevel": "medium",
    "result": "ZCFG_SUCCESS"
})


class TestLogin(unittest.TestCase):
    def setUp(self):
        MockSSHClient.reset()

        session = MockSSHSession()
        MockSSHClient.add_session("192.168.1.1",
                                  "admin",
                                  "testpassword",
                                  session)

    def test_correct_password(self):
        session = login("192.168.1.1", "admin", "testpassword")

        self.assertIsNotNone(session.current_session)

    def test_wrong_password(self):
        with self.assertRaises(InvalidPassword):
            login("192.168.1.1", "admin", "wrongpassword")

    def test_logout(self):
        session = login("192.168.1.1",
                        "admin",
                        "testpassword")

        logout(session)

        self.assertIsNone(session.current_session)
