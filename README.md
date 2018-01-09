[![PyPi](https://img.shields.io/pypi/v/pybots.svg)](https://pypi.python.org/pypi/pybots/)
[![Read The Docs](https://readthedocs.org/projects/pybots/badge/?version=latest)](http://pybots.readthedocs.io/en/latest/?badge=latest)
[![Known Vulnerabilities](https://snyk.io/test/github/dhondta/pybots/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/dhondta/pybots?targetFile=requirements.txt)
[![Python Versions](https://img.shields.io/pypi/pyversions/pybots.svg)](https://pypi.python.org/pypi/pybots/)
[![License](https://img.shields.io/pypi/l/pybots.svg)](https://pypi.python.org/pypi/pybots/)

# PyBots

This library aims to quickly write client bots for communicating with remote hosts in various ways.

It currently features the following bots: Socket & Web (generic), Netcat, HTTP, JSON, IRC, EPassport, RingZer0, Root-Me
  

## Installation

```
sudo pip install pybots
```


## Usage

Each bot class is implemented as a context manager and has a logger attached. It can thus be instantiated in a clear and straightforward way. Here is an example:

```py
from pybots import Netcat

with Netcat("remote_host", 1234) as bot:
    data = bot.send_receive("Hello!")
    # do something with data
```

Note that, if a bot is used behind a proxy, it will use system's proxy settings. This can be bypassed by using `no_proxy=True` while instantiating the bot.

```py
with Netcat("LAN_host", 1234, no_proxy=True) as bot:
    # ...
```


## CTF Examples

* [Hacky Easter 2017 (22 & 24)](doc/examples/hacky-easter-2017.md)
* [Hackvent 2017 (Day 06 & 10)](doc/examples/hackvent-2017.md)
* [RingZer0 / Coding (13 & 17)](doc/examples/ringzer0.md)
* [Root-Me / Programming](doc/examples/rootme.md)


## Contribution

For contributions or suggestions, please [open an Issue](https://github.com/dhondta/pybots/issues/new) and clearly explain, using an example or a use case if appropriate. 

If you want to get new bots added, please submit a Pull Request.
