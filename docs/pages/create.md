## Current Class Hierarchy

![](imgs/bots.png)

!!! note "Diagram not exhaustive"
    Some methods are not shown in this diagram as they are not necessary for developping new bots.

-----

## General-purpose bot

The following steps are the recommended way to build a new general-purpose bot:

1. Import the template and subclass it.

    ```python
    from pybots.base.template import Template
    
    class MyBot(Template):
        ...
    ```

2. Use `verbose` and `no_proxy` in constructor's signature then initialize the template first using them and finally call self-defined methods and assign attributes.

    ```python
    class MyBot(Template):
        def __init__(self, ..., verbose=False, no_proxy=False):
            super(MyBot, self).__init__(verbose, no_proxy)
            self.[...](...)
            self.[...] = ...
    ```

3. Write your private/protected methods (sorted in alphabetical order) for particular handling, not foreseen to be used when subclassing the bot for building specific-purpose ones.

    ```python
    class MyBot(Template):
        def __init__(self, ...):
            ...
        
        def __particular_handling(self, ...):
            ...
    ```

4. Write your public methods (sorted in alphabetical order) for use when subclassing the bot.

    ```python
    class MyBot(Template):
        def __init__(self, ...):
            ...
        
        def __particular_handling(self, ...):
            ...
            
        def something(self, ...):
            ...
    ```

5. If a `close` method is to be used for gracefully closing the bot (e.g. a socket), this should be a static method and the connection object should be bound (at initialization) to the class instead of `self` so that `signal.signal(signal.SIGINT, MyBot.close)` can be declared at the end of the file for redefining the key interruption signal processing function. Also, it should not be forgetted to put `Template.shutdown()` at the end of the `close` static method as `MyBot.close` will simply overwrite `Template.shutdown` (initial function passed to the signal) when redefining the signal. An exemple is provided hereafter:

    ```python
    class MyBot(Template):
        ...
        
        @staticmethod
        def close(exit=True):
            try:
                MyBot.connection.close()
            except:
                pass
            if exit:
                Template.shutdown()
    
    signal.signal(signal.SIGINT, MyBot.close)
    ```

6. Make extensive use of `self.logger` to log bot's actions for debugging (this will be very useful when creating more specific bots). Normally, each method should contain at least one call to `self.logger.debug` on average.

-----

## Specific-purpose bot - `IRCBot`

The following steps show how to create the `IRCBot` class:

1. First, the best-suited general-purpose bot for this is `SocletBot`, for managing a socket connection to the remote host.

    ```python
    from pybots.general.ssocket import SocketBot
    ```

2. The standard remote port for IRC is 6667 ; the argument can then be set with a default value.

    ```python
    class IRCBot(SocketBot):
        def __init__(self, host, port=6667
    ```

3. IRC bot's initialization requires to provide a nickname (e.g. by default `ircbot`), eventually a fullname (e.g. by default `IRC Bot`) and also a channel. Note that other arguments can be simply passed to the parent class (for handling verbose mode and proxy bypass).

    ```python
    class IRCBot(SocketBot):
        def __init__(self, host, port=6667, channel=None, nickname="ircbot",
             fullname="IRC Bot", *args, **kwargs):
    ```

4. Now that the signature is ready, the first thing to do is to initialize the general bot (handling the precomputation). Input arguments can eventually set as attributes.

    ```python
    class IRCBot(SocketBot):
        def __init__(self, host, port=6667, channel=None, nickname="ircbot",
                     fullname="IRC Bot", *args, **kwargs):
            super(IRCBot, self).__init__(host, port, *args, **kwargs)
            self.channel = channel
            self.nickname = nickname
            self.fullname = fullname
    ```

5. As `SocketBot` only initializes the required machinery, it is still necessary to connect to the remote host.

    ```python
    class IRCBot(SocketBot):
        def __init__(self, host, port=6667, channel=None, nickname="ircbot",
                     fullname="IRC Bot", *args, **kwargs):
            ...
            self.connect()
    ```

6. At this point, instead of using the `preamble` method (which can be left for application-specific bots), preamble actions can be written at the end of `__init__`. For the IRC protocol (explained in [RFC 2812](https://tools.ietf.org/html/rfc2812), several messages must be exchanged with the server in order to enter a chatroom

    ```python
    class IRCBot(SocketBot):
        def __init__(self, host, port=6667, channel=None, nickname="ircbot",
                     fullname="IRC Bot", *args, **kwargs):
            ...
            self.write("NICK {}".format(nickname))
            self.write("USER {} * * :{}".format(nickname, fullname))
            self.msg("nickserv", "iNOOPE")
    ```

7. Moreover, a channel can be joined if input. It can be handled with the ping message in a public method so that new channels can be joined during the execution of bot's context.

    ```python
    class IRCBot(SocketBot):
        def __init__(self, host, port=6667, channel=None, nickname="ircbot",
                     fullname="IRC Bot", *args, **kwargs):
            ...
            self.join(channel)

        def join(self, channel=None):
            if channel is not None:
                self.channel = channel
                self.write("JOIN {}".format(channel))
                self.buffer = self.read()
                if "PING " in self._hello:
                    pong = self.buffer.split("PING ")[1].strip()
                    self.write("PING {}".format(pong), eol="\r\n")  
                    self.buffer = self.read()
    ```

8. As private messages have a particular format, a public help method called `msg` can be added.

    ```python
    class IRCBot(SocketBot):
        ...
        def msg(self, dest, msg):
            self.write("PRIVMSG {} :{}".format(dest, msg), eol="\r\n")
    ```

9. Also, formal errors in the conversation itself can be reported, hence requiring the redefinition of the `read` method.

    ```python
    class IRCBot(SocketBot):
        ...
        def read(self, length=1024, disp=None):
            data = super(IRCBot, self).read(length, disp)
            if "ERROR" in data:
                self.logger.error(data.strip())
                SocketBot.close()
            return data
    ```

10. Finally, the bot should be documented appropriately and `self.logger.debug` should be extensively used for allowing debugging.

-----

## Application-related bot - `RootMeIRCBot`

The following steps show how to create the `RootMeIRCBot` class:

1. First, after reviewing *Programming* challenges from [Root-Me](https://www.root-me.org/), it can be figured out that the suited specific-purpose bot for these is `IRCBot`, for managing an IRC conversation.

    ```python
    from pybots.specific.irc import IRCBot
    ```

2. The URL for the website is provided and is standard as well as the channel. There only remains to define the challenge identification number and the username to be used. Also, an `answer` attribute can be created (for further use).

    ```python
    class RootMeIRCBot(IRCBot):
        def __init__(self, cid, username, *args, **kwargs):
            super(RootMeIRCBot, self).__init__("irc.root-me.org",
                channel="#root-me_challenge", nickname=username, *args, **kwargs)
            self.answer = None
            self.cid = int(cid)
    ```

3. There only remains to manage what happens before having the challenge data and what happens with the computed answer. This can be managed in the `preamble` and `postamble` methods. The succession of actions is determined by trial-and-error while using the bot embryo with `dips=True` as input argument in order to display the conversation and `verbose=True` to see the operations.

    ```python
    class RootMeIRCBot(IRCBot):
        ...
        def postamble(self):
            self.msg("candy", "!ep{} -rep {}".format(self.cid, self.answer))
            self.read_until("You dit it! You can validate the challenge"
                            " with the password")
            self.flag = self.buffer.strip()
            self.logger.info(self.flag)

        def preamble(self):
            pattern = "MODE {} +x".format(self.nickname)
            if pattern not in self.buffer:
                self.read_until(pattern)
            self.msg("candy", "!ep{}".format(self.cid))
            self.read_until("PRIVMSG {} :".format(self.nickname))
            self.inputs = {'message': self.buffer.strip()}
    ```

4. Finally, the bot should be documented appropriately.
