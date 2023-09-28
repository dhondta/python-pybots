## Introduction

The PyBots library aims to quickly write client bots for communicating with remote hosts in a standardized way using context managers.

The idea is to make creating client bots as easy as this (e.g. with debugging):

```python hl_lines="3 4 5"
from pybots import SampleBot

with SampleBot(ip_address, port, verbose=True) as bot:
    # do some computation
    # communicate with the remote host
```

-----

## Installation

This library is available on [PyPi](https://pypi.python.org/pypi/pybots/) and can be simply installed using Pip via `pip install pybots`.

-----

## Rationale

This library is born from the need of making computations while communicating the results to a remote host with time constraints. Furthermore, rewriting the same lines of code repeatedly for handling the session with the remote host while the computation could hold in only a few lines made scripting this kind of application a huge mess.

Hence, it was interesting to regroup some base features and machinery inside a few classes handling common protocols in a clean and modular way in order to hide the session-side and only let the computation-side for future scripts. This way, some classes could be particularized for handling more specific communications with security-related Web services (e.g. [Shodan](https://shodan.io), [Censys](https://censys.io)) or CTF websites (e.g. [RingZer0](https://ringzer0team.com), [Root-Me](https://www.root-me.org)).

-----

## Definitions

In the remainder of this documentation, the following terms are used:

- **Template**: The base class that holds non-network-related machinery (e.g. logging).

- **General-purpose bots**: The general classes, inheriting from the template, that handles network-related machinery regarding available/built-in Python packages.

- **Specific-purpose bots**: The specific classes, inheriting from general classes, that handles more particular protocols.

- **API classes**: The classes implementing full API's of Web services, relying on bots.

- **Application-related bots**: The particular classes, inheriting from specific classes, that abstract application-level communications with the target hosts.
