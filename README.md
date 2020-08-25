[![PyPi](https://img.shields.io/pypi/v/pybots.svg)](https://pypi.python.org/pypi/pybots/)
[![Read The Docs](https://readthedocs.org/projects/python-pybots/badge/?version=latest)](http://python-pybots.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/dhondta/python-pybots.svg?branch=master)](https://travis-ci.org/dhondta/python-pybots)
[![Requirements Status](https://requires.io/github/dhondta/python-pybots/requirements.svg?branch=master)](https://requires.io/github/dhondta/python-pybots/requirements/?branch=master)
[![Known Vulnerabilities](https://snyk.io/test/github/dhondta/python-pybots/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/dhondta/python-pybots?targetFile=requirements.txt)
[![Python Versions](https://img.shields.io/pypi/pyversions/pybots.svg)](https://pypi.python.org/pypi/pybots/)
[![License](https://img.shields.io/pypi/l/pybots.svg)](https://pypi.python.org/pypi/pybots/)

# PyBots

This library aims to quickly write client bots for communicating with remote hosts in a standardized way using context managers. It implements a few bots for some common protocols (HTTP, JSON, IRC, ...) and for communicating with specific applications (Shodan, Censys, HaveIBeenPwned?, RootMe, RingZer0, ...).
  

## Setup

```sh
pip install pybots
```

## Usage

Each bot class is implemented as a context manager and has a logger attached. It can thus be instantiated in a clear and straightforward way. Here is an example:

```py
from pybots import TCPBot

with TCPBot("remote_host", 1234) as bot:
    data = bot.send_receive("Hello!")
    # do something with data
```

Note that, if a bot is used behind a proxy, it will use system's proxy settings. This can be bypassed by using `no_proxy=True` while instantiating the bot.

```py
with TCPBot("LAN_host", 1234, no_proxy=True) as bot:
    # ...
```

## Examples

Real-Life Projects:

* [Bots Scheduler](https://github.com/dhondta/bots-scheduler) (uses [`ShodanBot`](https://github.com/dhondta/python-pybots/blob/master/pybots/bots/security/shodan.py), [`HaveIBeenPwnedBot`](https://github.com/dhondta/python-pybots/blob/master/pybots/bots/security/haveibeenpwned.py), [`GhostProjectBot`](https://github.com/dhondta/python-pybots/blob/master/pybots/bots/security/ghostproject.py) and a few others)

CTF:

* [Hacky Easter 2017 (22 & 24)](doc/examples/hacky-easter-2017.md)
* [Hackvent 2017 (Day 06 & 10)](doc/examples/hackvent-2017.md)
* [RingZer0 / Coding (13 & 17)](doc/examples/ringzer0.md)
* [Root-Me / Programming](doc/examples/rootme.md)
