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

import http.server
import logging

from . import InvalidPassword
from .devices import ZyxelBase
from .login import login
from .prometheus import prometheus
from paramiko.ssh_exception import SSHException
from time import sleep

# Set-up logging
logger = logging.getLogger(__name__)


class Scraper:
    def __init__(self, args):
        self.args = args
        self.session = None
        self.device = None

    def scrape(self):
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                if self.session is None:
                    self.session = login(self.args.host,
                                         self.args.user,
                                         self.args.passwd)

                self.device = ZyxelBase.get_device(self.session)

                xdsl = self.device.scrape_xdsl() \
                    if not self.args.ifconfig_only else None
                ifconfig = self.device.scrape_ifconfig() \
                    if not self.args.xdsl_only else None

                # Found what we need to, return
                return xdsl, ifconfig

            # Error handling
            except InvalidPassword as e:
                # Rethrow bad password exception
                raise e
            except SSHException as e:
                # Re-initialise the session (deal with "SSH session not active error")
                logger.warning(f"Retry [{attempt}/{max_attempts}]: SSHException: {e} after 100ms")
                try:
                    self.session = None
                    sleep(0.1)  # wait 100ms so we're not in a tight loop
                # Ignore any exceptions here, will be handled by the higher level retry loop
                except Exception as e: # noqa
                    pass

        # Failed to get the answer after 3 retries
        logger.error(f"Failed to retrieve data after {max_attempts} attempts")
        return None, None


class Handler(http.server.BaseHTTPRequestHandler):
    scraper = None

    def do_GET(self):
        if self.path == "/":
            self.send_index()
        elif self.path == "/metrics":
            self.send_metrics()
        else:
            self.send_error(404)

    def send_index(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write("""
<html>
<head><title>Zyxel Prometheus</title></head>
<body>
<h1>Zyxel Prometheus</h1>
<p><a href="/metrics">Metrics</a></p>
</body>
</html>""".encode("utf8"))

    def send_metrics(self):
        xdsl, ifconfig = self.scraper.scrape()
        # Todo: bit bodgy
        device = self.scraper.device

        self.send_response(200)
        self.end_headers()
        self.wfile.write(prometheus(xdsl, ifconfig, device).encode("utf8"))


def serve(args):  # pragma: no cover
    Handler.scraper = Scraper(args)
    server = http.server.HTTPServer(args.bind, Handler)
    server.serve_forever()
