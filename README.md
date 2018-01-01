[![pypi](https://img.shields.io/pypi/v/pybots.svg)](https://pypi.python.org/pypi/pybots/)
[![python](https://img.shields.io/pypi/pyversions/pybots.svg)](https://pypi.python.org/pypi/pybots/)
[![license](https://img.shields.io/pypi/l/pybots.svg)](https://pypi.python.org/pypi/pybots/)

# PyBots

This library aims to quickly write client bots for communicating with remote hosts in various ways.

It currently features:

- General-purpose bots:

  * Socket communication
  
- Specific-purpose bots:

  * Netcat-like
  * HTTP
  * JSON
  * IRC
  * EPassport (based on [`pypassport`](https://pypi.python.org/pypi/pypassport))

- CTF-related bots:

  * RingZer0
  * Root-Me
  

## Installation

```
sudo pip install pybots
```


## Usage

Each bot class is implemented as a context manager and has a basically configured logger attached. It can thus be instantiated in a clear and straightforward way. Here is an example:

```
from pybots.netcat import Netcat

class MyBot(Netcat):
    def precompute(self):
        self.lookup_table = ...

    def preamble(self):
        self.read_until('>')

with MyBot("remote_host", 1234) as bot:
    bot.write("Hello!")
    data = bot.read_until("hash: ")
    hash = data.split("hash: ")[-1]
    bot.write(bot.lookup_table[hash])
```

Note that, if a bot is used behind a proxy, it will use system's proxy settings. This can be bypassed by using `no_proxy=True` while instantiating the bot.

```
with MyBot("LAN_host", 1234, no_proxy=True) as bot:
    # ...
```


## CTF Examples

- Hacking Lab :

  * [Hacky Easter 2017 - Challenge 24](doc/examples/hacky-easter-2017-24.md)
  
- RingZer0 :

  * [Coding Challenges - Challenge 13](doc/examples/ringzer0-13.md)
  * [Coding Challenges - Challenge 17](doc/examples/ringzer0-17.md)

- Root-Me :

  * [Programming - Go back to college](doc/examples/rootme-programming-1.md)
  * [Programming - Uncompress me](doc/examples/rootme-programming-4.md)


## Bot Classes Hierarchy

<img src="doc/bots.png" width="80%"/>


## Contribution

For contributions or suggestions, please [open an Issue](https://github.com/dhondta/pybots/issues/new) and clearly explain, using an example or a use case if appropriate. 

If you want to get new bots added, please submit a Pull Request.
