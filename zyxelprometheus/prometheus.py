import re

line_rate_re = re.compile(
    r"Line Rate:\s+(?P<upstream>\d+[.]\d+) Mbps\s+"
    + r"(?P<downstream>\d+[.]\d+) Mbps")

#               Line Rate:      7.044 Mbps       39.998 Mbps
#    Actual Net Data Rate:      7.016 Mbps       39.999 Mbps
#          Trellis Coding:         ON                ON
#              SNR Margin:        5.3 dB            7.2 dB
#            Actual Delay:          0 ms              0 ms
#          Transmit Power:        2.2 dBm          11.4 dBm
#           Receive Power:       -6.5 dBm         -11.1 dBm
#              Actual INP:        0.0 symbols      55.0 symbols
#       Total Attenuation:        8.8 dB           22.6 dB
# Attainable Net Data Rate:      7.016 Mbps       47.811 Mbps


def prometheus(xdsl, traffic):
    output = []
    if xdsl is not None:
        line_rate = line_rate_re.search(xdsl)
        line_rate_up = int(float(line_rate.group("upstream"))*1024*1024)
        line_rate_down = int(float(line_rate.group("downstream"))*1024*1024)
        output.append("# HELP zyxel_line_rate The line rate.")
        output.append("# TYPE zyxel_line_rate gauge")
        output.append(f"""zyxel_line_rate{{stream="up"}} {line_rate_up}""")
        output.append(f"""zyxel_line_rate{{stream="down"}} {line_rate_down}""")

    if traffic is not None:
        iface_stats = traffic["Object"][0]["ipIfaceSt"]
        for name, idx in get_iface_names(traffic).items():
            bytes_sent = iface_stats[idx]["BytesSent"]
            bytes_recv = iface_stats[idx]["BytesReceived"]
            output.append("# HELP zyxel_bytes Bytes sent/received.")
            output.append("# TYPE zyxel_bytes counter")
            output.append(f"""zyxel_bytes{{stream="up",iface="{name}"}}"""
                          + f""" {bytes_sent}""")
            output.append(f"""zyxel_bytes{{stream="down",iface="{name}"}}"""
                          + f""" {bytes_recv}""")

            packets_sent = iface_stats[idx]["PacketsSent"]
            packets_recv = iface_stats[idx]["PacketsReceived"]
            output.append("# HELP zyxel_packets Packets sent/received.")
            output.append("# TYPE zyxel_packets counter")
            output.append(f"""zyxel_packets{{stream="up",iface="{name}"}}"""
                          + f""" {packets_sent}""")
            output.append(f"""zyxel_packets{{stream="down",iface="{name}"}}"""
                          + f""" {packets_recv}""")

    return "\n".join(output)


def get_iface_names(traffic):
    r = {}
    for idx in range(len(traffic["Object"][0]["ipIface"])):
        if traffic["Object"][0]["ipIface"][idx]["Status"] == "Up":
            r[traffic["Object"][0]["ipIface"][idx]["Name"].lower()] = idx
    return r
