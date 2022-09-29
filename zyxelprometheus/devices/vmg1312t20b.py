import logging
import re

from .zyxel import ZyxelBase

# Set-up logging
logger = logging.getLogger(__name__)


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
        r"near-end interleaved channel bit rate: (?P<downstream_interleaved>\d+) kbps.+"
        + r"near-end fast channel bit rate: (?P<downstream_fast>\d+) kbps.+"
        + r"far-end interleaved channel bit rate: (?P<upstream_interleaved>\d+) kbps.+"
        + r"far-end fast channel bit rate: (?P<upstream_fast>\d+) kbps", flags=re.MULTILINE | re.DOTALL)


    line_errors_re = re.compile(
        r"near-end FEC error interleaved: (?P<downstream_fec_errors>\d+).+" +
        r"near-end CRC error interleaved: (?P<downstream_crc_errors>\d+).+" +
        r"near-end HEC error interleaved: (?P<downstream_hec_errors>\d+).+" +
        r"far-end FEC error fast: (?P<upstream_fec_errors>\d+).+" +
        r"far-end CRC error fast: (?P<upstream_crc_errors>\d+).+" +
        r"far-end HEC error fast: (?P<upstream_hec_errors>\d+)"
        , flags=re.MULTILINE | re.DOTALL
    )

    def __init__(self, session=None):
        assert session is not None
        self._session = session

    def scrape_xdsl(self):
        stdin, stdout, stderr = self._session.exec_command("", get_pty=True)
        return self.execute("dsllinestatus", stdin, stdout)

    def scrape_ifconfig(self):
        stdin, stdout, stderr = self._session.exec_command("", get_pty=True)
        return self.execute("ifconfig", stdin, stdout)

    def parse_xdsl(self, xdsl):
        output = []
        if xdsl is not None:
            max_line_rate = self.max_line_rate_re.search(xdsl)
            if max_line_rate is not None:
                self.parse_xdsl_max_line_rate(max_line_rate, output)

            line_errors = self.line_errors_re.search(xdsl)
            if line_errors is not None:
                output.append(
                    "# HELP zyxel_line_errors The errors on the line.")
                output.append(
                    "# TYPE zyxel_line_errors counter")
                for direction in ["up", "down"]:
                    for error_type in ["fec", "crc", "hec"]:
                        error_rate = int(line_errors.group(f"{direction}stream_{error_type}_errors"))
                        output.append(
                            f"""zyxel_line_errors{{stream="{direction}", type="{error_type}"}} {error_rate}""")
        return output

    def parse_xdsl_max_line_rate(self, max_line_rate, output):
        line_rate_up_fast = int(max_line_rate.group("upstream_fast")) * 1000
        line_rate_up_interleaved = int(max_line_rate.group("upstream_interleaved")) * 1000
        line_rate_down_fast = int(max_line_rate.group("downstream_fast")) * 1000
        line_rate_down_interleaved = int(max_line_rate.group("downstream_interleaved")) * 1000

        logger.debug(f"down:{line_rate_down_interleaved} / {line_rate_down_fast}")
        logger.debug(f"up:{line_rate_up_interleaved} / {line_rate_up_fast}")

        # Use the max of fast / interleaved as the line speed.
        line_rate_up = max(line_rate_up_fast, line_rate_up_interleaved)
        line_rate_down = max(line_rate_down_fast, line_rate_down_interleaved)

        # Use the base class to format the main downstream / upstream info
        self.output_xdsl_max_line_rate(line_rate_down, line_rate_up, output)

        output.append(
            f"""zyxel_max_line_rate{{stream="up_fast"}} {line_rate_up_fast}""")
        output.append(
            f"""zyxel_max_line_rate{{stream="up_interleaved"}} {line_rate_up_interleaved}""")
        output.append(
            f"""zyxel_max_line_rate{{stream="down_fast"}} {line_rate_down_fast}""")
        output.append(
            f"""zyxel_max_line_rate{{stream="down_interleaved"}} {line_rate_down_interleaved}""")

