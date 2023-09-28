## General-purpose bots

<font size="4"><b>`SocketBot`</b></font>

This generic bot is mostly inspired from this [Gist](https://gist.github.com/leonjza/f35a7252babdf77c8421). It also handles system's proxy settings using an implementation inspired from this [recipe](http://code.activestate.com/recipes/577643-transparent-http-tunnel-for-python-sockets-to-be-u/).

![](imgs/bot-socketbot.png)

It can be instantiated using the following arguments:

**Argument** | **Default** | **Description**
--- | --- | ---
`host` |  | Hostname or IP address
`port` |  | Port number
`disp` | `False` | Display all exchanged messages
`verbose` | `False` | Verbose mode
`prefix` | `False` | Prefix messages for display (i.e. *[SRC]* for the server, *[BOT]* for the bot)
`no_proxy` | `False` | Force ignoring system proxy settings

When a SocketBot is instantiated, it only registers the input arguments as attributes and creates an empty buffer for collecting the received data. In order to initiate a communication, the `connect` method must be used. This way, the associated socket can be reconnected or connections to other remote hosts can be made with the same bot.

For communicating, the bot has six methods:

- `write`: for writing to the socket (using, by default, "\n" as the EOL character)
- `send`: alias for `write`
- `read`: for reading on the socket a given length of bytes
- `read_until`: for reading blocks until a given pattern is reached
- `receive`: alias for `read` and `read_until`
- `send_receive`: for combining `write` then `read_until`

Each time a read/write method is used, it returns the collected data.

An example of use of the SocketBot class is the Netcat bot (see next section).


<font size="4"><b>`WebBot`</b></font>

This generic bot aims to handle an HTTP session using predefined headers and relies on the `requests` library. It holds a `_request` attribute with the `requests.Request` instance and a `response` attribute with the `requests.Response` one. It has also a method for setting a cookie.

![](imgs/bot-webbot.png)

It can be instantiated using the following arguments:

**Argument** | **Default** | **Description**
--- | --- | ---
`url` |  | URL of the website (e.g. `http://example.com`)
`verbose` | `False` | Verbose mode
`no_proxy` | `False` | Force ignoring system proxy settings

For communicating, the bot has a few methods (the first being generic and the others being particularization of the first):

- `request`: generic method for requesting resources, holding a `method` argument for defining the HTTP method to be used
- `get`, `post`, `header`, `options`, `put`, `delete`: `request` method using `method=...`

At instantiation, HTTP-related methods are dynamically bound so that `get`, `post`, `header`, `options`, `put` and `delete` become available.

-----

## Protocol-related bots

<font size="4"><b>`TCPBot`</b></font>

This bot implements a Netcat-like bot that handles a single connection with a remote host, by default executing a preamble that reads from the server up to the first newline and displays the received data.

Here is an example:

```python
with TCPBot(ip_address, port) as nc:
    nc.write("Hello !")
```

Another example, redefining the preamble, writing with a different EOL character:

```python
class MyBot(TCPBot):
    def preamble(self):
        self.read_until(">")

with MyBot(ip_address, port) as nc:
    nc.write("dir", eol="\r\n")
```

<font size="4"><b>`IRCBot`</b></font>

This bot aims to manage conversations on an IRC server using a `msg` method. It connects and sends user's data (by default, the nickname is `ircbot` and the full name is `IRC Bot`). It then executes the user-defined preamble and finally tries to connect to the input channel.

```python
class MyIRCBot(IRCBot):
    def preamble(self):
        self.msg("hellosrv", "HELLO")

with MyIRCBot(ip_address, port, channel="#a_channel") as irc:
    irc.msg("all", "Hello world!")
```

<font size="4"><b>`HTTPbot`</b></font>

This bot is an inherited class of the WebBot in that it adds a parsing of the current response using [`BeautifulSoup`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/), stored in a new `soup` attribute.

```python
with HTTPBot(url) as bot:
    bot.get("/")
    print(bot.soup.prettify())
```

<font size="4"><b>`JSONBot`</b></font>

This bot is an inherited class of the WebBot in that it adds a parsing of the current response using the `json` built-in module, stored in a new `json` attribute. Also, while initializing, it automatically adds the right `Content-Type` HTTP header so that the bot communicates with JSON objects.

```python
with JSONBot(url) as bot:
    bot.get("/")
    print(bot.json)
```

-----

## API definition classes

<font size="4"><b>`API`</b></font>

This class allows to define RESTful API's using HTTP or JSON. It handles caching of request results for sparing exchanges with the remote API's. This is done in combination with multiple method decorators that aim to successfully communicate.

**Name** | **Parameters** | **Description**
--- | --- | ---
`apicall` |  | This flags a method as an API call ; required for caching
`cache` | `duration` (seconds) | This allows to define a caching duration after which the entry is expired and removed
`invalidate` | `other_function` | This 
`private` |  | This is aimed to flag a method as only usable in private (or paid, or with an API plan) mode
`time_throttle` | `min_duration`, `max_duration`, `n_requests` | defines time throttling 


<font size="4"><b>`SearchAPI`</b></font>


