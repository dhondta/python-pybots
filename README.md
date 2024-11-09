<p align="center"><img src="https://github.com/dhondta/python-pybots/raw/main/docs/pages/imgs/logo.png"></p>
<h1 align="center">PyBots <a href="https://twitter.com/intent/tweet?text=PyBots%20-%20Devkit%20for%20quickly%20creating%20client%20bots%20for%20remote%20communications.%0D%0APython%20library%20for%20writing%20client%20bots%20relying%20on%20common%20protocols%20(HTTP,%20JSON,%20IRC,%20...).%0D%0Ahttps%3a%2f%2fgithub%2ecom%2fdhondta%2fpython-pybots%0D%0A&hashtags=python,programming,devkit,bot,client,cli,http,tcp,ctftools"><img src="https://img.shields.io/badge/Tweet--lightgrey?logo=twitter&style=social" alt="Tweet" height="20"/></a></h1>
<h3 align="center">Create your robot clients with Python.</h3>

[![PyPi](https://img.shields.io/pypi/v/pybots.svg)](https://pypi.python.org/pypi/pybots/)
[![Read The Docs](https://readthedocs.org/projects/python-pybots/badge/?version=latest)](http://python-pybots.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://github.com/dhondta/python-pybots/actions/workflows/python-package.yml/badge.svg)](https://github.com/dhondta/python-pybots/actions/workflows/python-package.yml)
[![Python Versions](https://img.shields.io/pypi/pyversions/pybots.svg)](https://pypi.python.org/pypi/pybots/)
[![Known Vulnerabilities](https://snyk.io/test/github/dhondta/python-pybots/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/dhondta/python-pybots?targetFile=requirements.txt)
[![License](https://img.shields.io/pypi/l/pybots.svg)](https://pypi.python.org/pypi/pybots/)

This library aims to quickly write client bots for communicating with remote hosts in a standardized way using context managers. It implements a few bots for some common protocols (HTTP, JSON, IRC, ...) and for communicating with specific applications (Shodan, Censys, HaveIBeenPwned?, RootMe, RingZer0, ...).

```sh
pip install pybots
```

## :sunglasses: Usage

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

## :ghost: Supported Bots

### Generic Purpose

All the following bots use the same interface providing uniformized logging.

**Name** |  **Description**
:----------:|---------------------------------------------------------------
HTTP | For browsing and parsing a Web page with BeautifulSoup
IRC | For connecting to an IRC server on a given channel with a given nickname
JSON | For dealing with a JSON API
TCP | For opening a TCP socket


### CTF Platforms

Each of these bots is aimed to parse inputs from a challenge and to send the answer computed in the context of the bot to the target website for retrieving the flag.

**Name** |  **Description**
:----------:|---------------------------------------------------------------
RingZer0 | Web bot for all kinds of challenges
RootMe | IRC bot for programming challenges
ZSIS | Web bot for progrmming challenges


### Security Services

These bots are built upon an API layer that defines corresponding interfaces to the online services' functionalities as described in their documentation. The bots implement common operations that may involve multiple calls to the online services' API.

**Name** |  **Description**
:----------:|---------------------------------------------------------------
Censys | JSON bot that checks for IP's and domains
Ghost Project | Web bot that checks for emails
HaveIBeenPwned? | JSON bot that checks for emails and passwords
HaveIBeenSold? | JSON bot that checks for emails
Nuclear Leaks | Web bot that checks for emails and domains
Shodan | JSON bot that checks for IP's

### Utility Services

**Name** |  **Description**
:----------:|---------------------------------------------------------------
Git | Web bot that can retrieve a Git repository
PostBin | Web bot that can perform Bin operations

## :mag: Examples

### Real-Life Projects

* [Bots Scheduler](https://github.com/dhondta/bots-scheduler/) (uses [`ShodanBot`](https://github.com/dhondta/python-pybots/blob/main/src/pybots/bots/security/shodan.py), [`HaveIBeenPwnedBot`](https://github.com/dhondta/python-pybots/blob/main/src/pybots/bots/security/haveibeenpwned.py), [`GhostProjectBot`](https://github.com/dhondta/python-pybots/blob/main/src/pybots/bots/security/ghostproject.py) and a few others)

### CTF

* [Hackvent 2017 (Day 06 & 10)](https://github.com/dhondta/python-pybots/blob/main/docs/pages/examples/hackvent-2017.md)
* [RingZer0 / Coding (13 & 17)](https://github.com/dhondta/python-pybots/blob/main/docs/pages/examples/ringzer0.md)
* [Root-Me / Programming](https://github.com/dhondta/python-pybots/blob/main/docs/pages/examples/rootme.md)


## :clap:  Supporters

[![Stargazers repo roster for @dhondta/python-pybots](https://reporoster.com/stars/dark/dhondta/python-pybots)](https://github.com/dhondta/python-pybots/stargazers)

[![Forkers repo roster for @dhondta/python-pybots](https://reporoster.com/forks/dark/dhondta/python-pybots)](https://github.com/dhondta/python-pybots/network/members)

<p align="center"><a href="#"><img src="https://img.shields.io/badge/Back%20to%20top--lightgrey?style=social" alt="Back to top" height="20"/></a></p>
