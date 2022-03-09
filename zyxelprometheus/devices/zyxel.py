import time
import re


class ZyxelBase:
    PROMPT = "ZySH> "

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

    def _read_to(self, stdout, readto):
        endtime = time.time() + 5
        chars = []
        lreadto = list(readto)
        while not stdout.channel.eof_received:
            char = stdout.read(1).decode("utf8")
            if char != "":
                chars.append(char)
                if chars[-len(readto):] == lreadto:
                    return "".join(chars[:-len(readto)])
            if time.time() > endtime:
                stdout.channel.close()
                break
        return "".join(chars)

    def parse_xdsl(self, xdsl):
        raise NotImplementedError

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

    # def parse_ifconfig(self, ifconfig):
    #     raise NotImplementedError

    def parse_xdsl_max_line_rate(self, max_line_rate, output):
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

