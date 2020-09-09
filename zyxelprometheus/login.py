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

import paramiko
from paramiko.client import SSHClient
from paramiko.ssh_exception import AuthenticationException

from .exceptions import InvalidPassword


def login(host, username, password):
    session = SSHClient()
    session.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        session.connect(hostname=host, username=username, password=password)
    except AuthenticationException:
        raise InvalidPassword()

    return session


def logout(session):
    session.close()
