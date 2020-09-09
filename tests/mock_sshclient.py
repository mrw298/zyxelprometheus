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

from paramiko.ssh_exception import AuthenticationException, \
                                   NoValidConnectionsError

PROMPT = "ZySH> ".encode("utf8")


class MockSSHClient:
    mock_sessions = {}

    def __init__(self):
        self.missing_host_key_policy = None
        self.current_session = None

    def connect(self, hostname, username, password):
        if (hostname, username, password) in self.mock_sessions:
            self.current_session = self.mock_sessions[(hostname,
                                                       username,
                                                       password)]
            return

        for session_key in self.mock_sessions.keys():
            if hostname == session_key[0]:
                raise AuthenticationException("Authentication failed.")
        raise NoValidConnectionsError({(hostname, 22): True})

    def set_missing_host_key_policy(self, policy):
        self.missing_host_key_policy = policy

    def exec_command(self, cmd, get_pty=False):
        return self.current_session, self.current_session, None

    def close(self):
        self.current_session = None

    @classmethod
    def reset(cls):
        cls.mock_sessions = {}

    @classmethod
    def add_session(cls, host, user, password, session):
        cls.mock_sessions[(host, user, password)] = session


class MockSSHSession:
    def __init__(self):
        self.cmds = {}
        self.channel = MockChannel()

        self.recv_buffer = PROMPT

    def add_cmd(self, cmd, response):
        self.cmds[cmd] = response.encode("utf8")

    def write(self, cmd):
        if cmd in self.cmds:
            self.recv_buffer = self.cmds[cmd]
        else:
            raise ValueError(f"Unset command used. {repr(cmd)}")

    def read(self, count):
        if len(self.recv_buffer) <= count:
            data = self.recv_buffer
            self.recv_buffer = PROMPT
            return data
        else:
            data = self.recv_buffer[:count]
            self.recv_buffer = self.recv_buffer[count:]
            return data


class MockChannel:
    def __init__(self):
        self.eof_received = False
