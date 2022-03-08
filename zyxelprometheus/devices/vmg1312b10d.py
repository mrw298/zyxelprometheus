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

    # br0       Link encap:Ethernet  HWaddr E4:18:6B:06:87:70
    #           inet addr:192.168.1.1  Bcast:192.168.1.255  Mask:255.255.255.0
    #           inet6 addr: fe80::e618:6bff:fe06:8770/64 Scope:Link
    #           UP BROADCAST RUNNING ALLMULTI MULTICAST  MTU:1500  Metric:1
    #           RX packets:7968422 errors:0 dropped:19510 overruns:0 frame:0
    #           TX packets:11495200 errors:0 dropped:0 overruns:0 carrier:0
    #           collisions:0 txqueuelen:0
    #           RX bytes:2713281739 (2.5 GiB)  TX bytes:1342943018 (1.2 GiB)

    iface_re = re.compile(r"^([\w.]+)\s+(.*?)^$", re.MULTILINE | re.DOTALL)

    packets_re = re.compile(r"(RX|TX) packets:(\d+)")
    errors_re = re.compile(r"(RX|TX).*errors:(\d+)")
    dropped_re = re.compile(r"(RX|TX).*dropped:(\d+)")

    bytes_re = re.compile(r"(RX|TX) bytes:(\d+)")

    iface_stats_map = [
        ("zyxel_bytes", "Bytes sent/received.", bytes_re),
        ("zyxel_packets", "Bytes sent/received.", packets_re),
        ("zyxel_errors", "Bytes sent/received.", errors_re),
        ("zyxel_dropped", "Bytes sent/received.", dropped_re),
    ]

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

            max_line_rate = self.max_line_rate_re.search(xdsl)
            line_rate_up = int(max_line_rate.group("upstream")) * 1000
            line_rate_down = int(max_line_rate.group("downstream")) * 1000
            output.append(
                "# HELP zyxel_max_line_rate The maxiumum attainable line rate.")
            output.append(
                "# TYPE zyxel_max_line_rate gauge")
            output.append(
                f"""zyxel_max_line_rate{{stream="up"}} {line_rate_up}""")
            output.append(
                f"""zyxel_max_line_rate{{stream="down"}} {line_rate_down}""")
        return output

    def parse_ifconfig(self, ifconfig):
        output = []
        if ifconfig is not None:
            for (metric, help, metric_re) in self.iface_stats_map:
                output.append(f"# HELP {metric} {help}")
                output.append(f"# TYPE {metric} counter")
                for iface in self.iface_re.finditer(ifconfig.replace("\r\n", "\n")):
                    iface_name = iface.group(1)
                    iface_stats = iface.group(2)
                    for groups in metric_re.finditer(iface_stats):
                        metric_stream = groups.group(1).lower()
                        metric_value = int(groups.group(2))
                        output.append(
                            f"""{metric}{{stream="{metric_stream}","""
                            + f"""iface="{iface_name}"}} {metric_value}""")

        return output
