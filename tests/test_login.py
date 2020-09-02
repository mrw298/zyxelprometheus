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

from zyxelprometheus import login, logout, InvalidPassword

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
    @responses.activate
    def test_correct_password(self):
        responses.add(responses.POST, 'https://192.168.1.1/UserLogin',
                      body=RESPONSE,
                      status=200)

        login("https://192.168.1.1", "admin", "testpassword")

        self.assertEqual(1, len(responses.calls))
        data = json.loads(responses.calls[0].request.body)
        self.assertEqual("admin", data["Input_Account"])
        self.assertEqual(b"testpassword", b64decode(data["Input_Passwd"]))

    @responses.activate
    def test_wrong_password(self):
        responses.add(responses.POST, 'https://192.168.1.1/UserLogin',
                      status=401)

        with self.assertRaises(InvalidPassword):
            login("https://192.168.1.1", "admin", "testpassword")

        self.assertEqual(1, len(responses.calls))
        data = json.loads(responses.calls[0].request.body)
        self.assertEqual("admin", data["Input_Account"])
        self.assertEqual(b"testpassword", b64decode(data["Input_Passwd"]))

    @responses.activate
    def test_correct_password(self):
        responses.add(responses.POST, 'https://192.168.1.1/UserLogin',
                      body=RESPONSE,
                      status=200)
        responses.add(responses.POST,
                      "https://192.168.1.1/cgi-bin/UserLogout?"
                      + "sessionkey=816284860",
                      status=200)

        session, sessionkey = login("https://192.168.1.1",
                                    "admin",
                                    "testpassword")

        # This will raise a ConnectionError if we hit the wrong url.
        logout(session, "https://192.168.1.1", sessionkey)
