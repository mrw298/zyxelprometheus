import re

from .zyxel import ZyxelBase


class VMG1312T20B(ZyxelBase):
    # =============================================================================
    #     xDSLFwVersion:      FwVer:5.10.6.0_B_A60901 HwVer:T14.F7_0.0
    #        Line State:      Up
    #        Modulation:      ITU G.993.2(VDSL2), G.998.4(G.I
    #        Annex Mode:      ANNEX_B
    # =============================================================================
    #
    # TPSTC type: 64/65B PTM TC
    #
    # near-end interleaved channel bit rate: 27397 kbps
    # near-end fast channel bit rate: 0 kbps
    # far-end interleaved channel bit rate: 0 kbps
    # far-end fast channel bit rate: 4294 kbps
    #
    # near-end FEC error fast: 0
    # near-end FEC error interleaved: 599876
    # near-end CRC error fast: 0
    # near-end CRC error interleaved: 0
    # near-end HEC error fast: 0
    # near-end HEC error interleaved: 0
    # far-end FEC error fast: 61
    # far-end FEC error interleaved: 0
    # far-end CRC error fast: 0
    # far-end CRC error interleaved: 0
    # far-end HEC error fast: 0
    # far-end HEC error interleaved: 0
    # DSL uptime : 9:07, 17 secs
    # DSL activetime :0 min, 15 secs
    #
    # Downstream:
    # relative capacity occupation: 100%
    # noise margin downstream: 7.4 dB
    # output power upstream: 7.0 dbm
    # attenuation downstream: 21.8 dB
    #
    # Upstream:
    # relative capacity occupation: 100%
    # noise margin upstream: 8.1 dB
    # output power downstream: 12.1 dbm
    # attenuation upstream: 6.6 dB
    #
    # Bit table:
    # carrier load: number of bits per tone
    # tone   0- 31: 00 00 00 09 ab bc dd dd dd dd dd dc cb bb a9 87
    # tone  32- 63: 6a 99 88 77 78 99 99 6a aa ab bb bb cc cc cc cc
    # tone  64- 95: cc cc cc cc cc cc cc cc cc cc cc cc cc cc cc cc
    # tone  96-127: cc dc cc dd dc cc cc cc cc cc cc cc cc bc cc cb
    # tone 128-159: cc cc cb cb cc cc cc cc cc bb bb bb bb bb bb cc
    # tone 160-191: ba bb bb bb bb bb bb bb bb bb bb bb bb bb ba ba
    # tone 192-223: bb ba ba ba aa aa aa aa aa aa aa aa aa aa aa aa
    # tone 224-255: aa aa aa ab aa aa aa aa aa aa 9a aa 9a aa aa aa

    max_line_rate_re = re.compile(
        r"near-end interleaved channel bit rate: (?P<downstream>\d+) kbps.+"
        + r"far-end fast channel bit rate: (?P<upstream>\d+) kbps", flags=re.MULTILINE | re.DOTALL)

    line_errors_re = re.compile(
        r"near-end FEC error interleaved: (?P<downstream_fec_errors>\d+).+" +
        r"near-end CRC error interleaved: (?P<downstream_crc_errors>\d+).+" +
        r"near-end HEC error interleaved: (?P<downstream_hec_errors>\d+).+" +
        r"far-end FEC error fast: (?P<upstream_fec_errors>\d+).+" +
        r"far-end CRC error fast: (?P<upstream_crc_errors>\d+).+" +
        r"far-end HEC error fast: (?P<upstream_hec_errors>\d+)"
        , flags=re.MULTILINE | re.DOTALL
    )

    # line_rate_re = re.compile(
    #     r"Bearer:\s+(?P<bearer>\d), Upstream rate = (?P<upstream>\d+) Kbps,\s+"
    #     + r"Downstream rate = (?P<downstream>\d+) Kbps")

    # br0       Link encap:Ethernet  HWaddr EC:3E:B3:E3:D5:C0
    #           inet addr:192.168.1.1  Bcast:192.168.1.255  Mask:255.255.255.0
    #           inet6 addr: fe80::ee3e:b3ff:fee3:d5c0/64 Scope:Link
    #           UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
    #           RX packets:106063 errors:0 dropped:0 overruns:0 frame:0
    #           TX packets:29208 errors:0 dropped:0 overruns:0 carrier:0
    #           collisions:0 txqueuelen:0
    #           RX bytes:27056367 (25.8 MiB)  TX bytes:6642360 (6.3 MiB)

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
        return self.execute("dsllinestatus", stdin, stdout)

    def scrape_ifconfig(self):
        stdin, stdout, stderr = self._session.exec_command("", get_pty=True)
        return self.execute("ifconfig", stdin, stdout)

    def parse_xdsl(self, xdsl):
        output = []
        if xdsl is not None:
            # for line_rate in self.line_rate_re.finditer(xdsl):
            #     bearer = int(line_rate.group("bearer"))
            #     line_rate_up = int(line_rate.group("upstream")) * 1000
            #     line_rate_down = int(line_rate.group("downstream")) * 1000
            #     if line_rate_up == 0 and line_rate_down == 0:
            #         continue
            #     output.append("# HELP zyxel_line_rate The line rate.")
            #     output.append("# TYPE zyxel_line_rate gauge")
            #     output.append(f"""zyxel_line_rate{{bearer=\"{bearer}\","""
            #                   + f"""stream="up"}} {line_rate_up}""")
            #     output.append(
            #         f"""zyxel_line_rate{{bearer=\"{bearer}\",stream="down"}}"""
            #         + f""" {line_rate_down}""")

            max_line_rate = self.max_line_rate_re.search(xdsl)
            if max_line_rate is not None:
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

            line_errors = self.line_errors_re.search(xdsl)
            if line_errors is not None:
                output.append(
                    "# HELP zyxel_line_errors The errors on the line.")
                output.append(
                    "# TYPE zyxel_line_errors counter")
                for direction in ["upstream", "downstream"]:
                    for error_type in ["fec", "crc", "hec"]:
                        error_rate = int(line_errors.group(f"{direction}_{error_type}_errors"))
                        output.append(
                            f"""zyxel_line_errors{{stream="{direction}", type="{error_type}"}} {error_rate}""")
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
