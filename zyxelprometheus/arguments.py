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

import argparse
import os

from .exceptions import InvalidArguments

parser = argparse.ArgumentParser(
    description='Collect statistics from a Zyxel router and present them to '
    + 'Prometheus.')
parser.add_argument('--host', type=str, nargs='?',
                    default="https://192.168.1.1",
                    help='the host name to connect to '
                    + '(must start with https://)')
parser.add_argument('--user', type=str, nargs='?', default="admin",
                    help='the user name to use (can also be set with '
                    + '$ZYXEL_USER)')
parser.add_argument('--passwd', type=str, nargs='?',
                    help='the password to use (can also be set with '
                    + '$ZYXEL_PASSWD)')
parser.add_argument('--bind', type=str, nargs='?', default="0.0.0.0:9100",
                    help='the ip address and port to bind to when running '
                    + 'in server mode (-d)')
parser.add_argument('-d', '--serve', action="store_true", default=False,
                    help='run in server mode, collecting the statistics '
                    + 'each time /metrics is requested')
parser.add_argument('--raw', action="store_true", default=False,
                    help='prints out the raw values collected from the '
                    + 'router and exits')
parser.add_argument('--traffic-only', action="store_true", default=False,
                    help='only requests traffic data')
parser.add_argument('--xdsl-only', action="store_true", default=False,
                    help='only requests XDSL data')


def get_arguments(args):
    args = parser.parse_args(args)
    if "ZYXEL_USER" in os.environ:
        args.user = os.environ["ZYXEL_USER"]
    if "ZYXEL_PASSWD" in os.environ:
        args.passwd = os.environ["ZYXEL_PASSWD"]

    if args.passwd is None:
        raise InvalidArguments("No password supplied. Either use --passwd "
                               + "or set $ZYXEL_PASSWD")

    if args.serve and args.raw:
        raise InvalidArguments("Can't use raw mode when serving mode is "
                               + "turned on.")

    if ":" not in args.bind:
        args.bind = (args.bind, 9100)
    else:
        args.bind = (args.bind.split(":")[0], int(args.bind.split(":")[1]))

    return args
