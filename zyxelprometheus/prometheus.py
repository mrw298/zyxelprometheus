import re

line_rate_re = re.compile(r"Line Rate:\s+(?P<upstream>\d+[.]\d+) Mbps\s+(?P<downstream>\d+[.]\d+) Mbps")

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
    line_rate = line_rate_re.search(xdsl)
    line_rate_up = int(float(line_rate.group("upstream"))*1024*1024)
    line_rate_down = int(float(line_rate.group("downstream"))*1024*1024)
    output.append("# HELP zyxel_line_rate The line rate.")
    output.append("# TYPE zyxel_line_rate gauge")
    output.append(f"""zyxel_line_rate{{stream="up"}} {line_rate_up}""")
    output.append(f"""zyxel_line_rate{{stream="down"}} {line_rate_down}""")

    return "\n".join(output)
