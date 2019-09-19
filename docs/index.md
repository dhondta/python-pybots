## Introduction

The PyBots library aims to quickly write client bots for communicating with remote hosts in various ways using the power of context managers.

The idea is to make creating client bots as easy as this:

``` python hl_lines="3 4 5"
from pybots import SampleBot

with SampleBot(ip_address, port, ...) as bot:
    # do some computation
    # communicate with the remote host
```

-----

## Installation

This library is available on [PyPi](https://pypi.python.org/pypi/pybots/) and can be simply installed using Pip via `sudo pip install pybots`.

-----

## Rationale

This library is born from the need of making computations while communicating the results to a remote host with time constraints. Furthermore, rewriting the same lines of code repeatedly for handling the session with the remote host while the computation could hold in only a few lines made scripting this kind of application a huge mess.

Hence, it was interesting to regroup some base features and machinery inside a few classes handling common protocols in a clean and modular way in order to hide the session-side and only let the computation-side for future scripts.

In the funny part of such applications, it was also interesting to particularize these classes for handling more specific communications with CTF websites like [RingZer0](https://ringzer0team.com) and [Root-Me](https://www.root-me.org). This allowed to reduce the size of challenge solution scripts to a minimum for only the computation part.

-----

## Definitions

In the remainder of this documentation, the following terms are used:

- **Template**: The base class that holds non-network-related machinery (e.g. logging).

- **General-purpose bots**: The general classes, inheriting from the template, that handles network-related machinery regarding available/built-in Python packages.

- **Specific-purpose bots**: The specific classes, inheriting from general classes, that handles more particular protocols.

- **Application-related bots**: The particular classes, inheriting from specific classes, that abstract application-level communications with the target hosts (e.g. CTF-related bots for communicating with CTF websites).
