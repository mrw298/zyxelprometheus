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

import time

PROMPT = "ZySH> "


def _read_to_prompt(stdout):
    endtime = time.time() + 5
    chars = []
    prompt = list(PROMPT)
    while not stdout.channel.eof_received:
        char = stdout.read(1).decode("utf8")
        if char != "":
            chars.append(char)
            if chars[-len(prompt):] == prompt:
                return "".join(chars[:-len(prompt)])
        if time.time() > endtime:
            stdout.channel.close()
            break
    return "".join(chars)


def scrape_xdsl(session):
    stdin, stdout, stderr = session.exec_command("", get_pty=True)
    _read_to_prompt(stdout)
    stdin.write("xdslctl info\n")
    return _read_to_prompt(stdout)


def scrape_ifconfig(session):
    stdin, stdout, stderr = session.exec_command("", get_pty=True)
    _read_to_prompt(stdout)
    stdin.write("ifconfig\n")
    return _read_to_prompt(stdout)
