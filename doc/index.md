## Introduction

The PyBots library aims to quickly write client bots for communicating with remote hosts in various ways using the power of context managers.

The idea is to make creating client bots as easy as this:

```
from pybots import SampleBot

with SampleBot(...) as bot:
    # do some computation
```


## Installation

This library is available on [PyPi](https://pypi.python.org/pypi/pybots/) and can be simply installed using Pip.

```
sudo pip install pybots
```
