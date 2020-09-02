# zyxelprometheus

[![Build Status](https://travis-ci.com/andrewjw/zyxelprometheus.svg?branch=master)](https://travis-ci.com/andrewjw/zyxelprometheus)
[![Coverage Status](https://coveralls.io/repos/github/andrewjw/zyxelprometheus/badge.svg?branch=master)](https://coveralls.io/github/andrewjw/zyxelprometheus?branch=master)
[![PyPI version](https://badge.fury.io/py/zyxelprometheus.svg)](https://badge.fury.io/py/zyxelprometheus)

Get statistics from a Zyxel router and expose them to Prometheus.

## Running

```zyxelprometheus [-h] [--host [HOST]] [--user [USER]]
                       [--passwd [PASSWD]] [--bind [BIND]] [-d] [--raw]
                       [--traffic-only] [--xdsl-only]

optional arguments:
  -h, --help         show this help message and exit
  --host [HOST]      the host name to connect to (must start with https://)
  --user [USER]      the user name to use (can also be set with $ZYXEL_USER)
  --passwd [PASSWD]  the password to use (can also be set with $ZYXEL_PASSWD)
  --bind [BIND]      the ip address and port to bind to when running in server
                     mode (-d)
  -d, --serve        run in server mode, collecting the statistics each time
                     /metrics is requested
  --raw              prints out the raw values collected from the router and
                     exits
  --traffic-only     only requests traffic data
  --xdsl-only        only requests XDSL data
```
