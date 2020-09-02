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

from base64 import b64encode
import json

import requests

from .exceptions import InvalidPassword

# https://192.168.1.1/UserLogin
# {"Input_Account":"admin","Input_Passwd":"c2hhZ2dpZTE:",
#  "currLang":"en","RememberPassword":0,"SHA512_password":false}
#
# Response:
# {"sessionkey":816284860,"ThemeColor":"","changePw":false,
# "showSkipBtn":false,"quickStart":false,"loginAccount":"admin",
# "loginLevel":"medium","result":"ZCFG_SUCCESS"}


def login(host, username, password):
    session = requests.session()
    session.verify = False
    r = session.post(host + "/UserLogin", data=json.dumps({
        "Input_Account": "admin",
        "Input_Passwd": b64encode(password.encode("utf8")).decode("utf8"),
        "currLang": "en",
        "RememberPassword": 0,
        "SHA512_password": False
    }))
    if r.status_code == 401:
        raise InvalidPassword("Invalid username or password.")
    r.raise_for_status()

    return session, r.json()["sessionkey"]


# /cgi-bin/UserLogout?sessionkey=816284860
def logout(session, host, sessionkey):
    r = session.post(host + f"/cgi-bin/UserLogout?sessionkey={sessionkey}")
    r.raise_for_status()
