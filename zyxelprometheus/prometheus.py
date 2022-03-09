import re

from .devices import ZyxelBase


def prometheus(xdsl, ifconfig, device: ZyxelBase):

    output = [*device.parse_xdsl(xdsl), *device.parse_ifconfig(ifconfig)]
    return "\n".join(output)
