import re

from .zyxel import ZyxelBase


class VMG1312B10D(ZyxelBase):
    # xdslctl: ADSL driver and PHY status
    # Status: Showtime
    # Last Retrain Reason:	0
    # Last initialization procedure status:	0
    # Max:	Upstream rate = 7833 Kbps, Downstream rate = 47522 Kbps
    # Bearer:	0, Upstream rate = 7833 Kbps, Downstream rate = 39999 Kbps
    # Bearer:	1, Upstream rate = 0 Kbps, Downstream rate = 0 Kbps

    max_line_rate_re = re.compile(
        r"Max:\s+Upstream rate = (?P<upstream>\d+) Kbps,\s+"
        + r"Downstream rate = (?P<downstream>\d+) Kbps")

    line_rate_re = re.compile(
        r"Bearer:\s+(?P<bearer>\d), Upstream rate = (?P<upstream>\d+) Kbps,\s+"
        + r"Downstream rate = (?P<downstream>\d+) Kbps")

    def __init__(self, session=None):
        assert session is not None
        self._session = session

    def execute(self, cmd, stdin, stdout):
        self._read_to(stdout, self.PROMPT)
        stdin.write(cmd + "\n")
        self._read_to(stdout, cmd + "\r\n")
        return self._read_to(stdout, self.PROMPT)

    def scrape_xdsl(self):
        stdin, stdout, stderr = self._session.exec_command("", get_pty=True)
        return self.execute("xdslctl info", stdin, stdout)

    def scrape_ifconfig(self):
        stdin, stdout, stderr = self._session.exec_command("", get_pty=True)
        return self.execute("ifconfig", stdin, stdout)

    def parse_xdsl(self, xdsl):
        output = []
        if xdsl is not None:
            for line_rate in self.line_rate_re.finditer(xdsl):
                bearer = int(line_rate.group("bearer"))
                line_rate_up = int(line_rate.group("upstream")) * 1000
                line_rate_down = int(line_rate.group("downstream")) * 1000
                if line_rate_up == 0 and line_rate_down == 0:
                    continue
                output.append("# HELP zyxel_line_rate The line rate.")
                output.append("# TYPE zyxel_line_rate gauge")
                output.append(f"""zyxel_line_rate{{bearer=\"{bearer}\","""
                              + f"""stream="up"}} {line_rate_up}""")
                output.append(
                    f"""zyxel_line_rate{{bearer=\"{bearer}\",stream="down"}}"""
                    + f""" {line_rate_down}""")

            # Get the max line rate
            max_line_rate = self.max_line_rate_re.search(xdsl)
            self.parse_xdsl_max_line_rate(max_line_rate, output)

        return output
