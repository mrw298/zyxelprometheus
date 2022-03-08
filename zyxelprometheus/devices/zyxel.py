import time


class ZyxelBase:
    PROMPT = "ZySH> "

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
        raise NotImplementedError
