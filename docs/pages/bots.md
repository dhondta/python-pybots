## Security Web service bots

<font size="4"><b>`CensysBot`</b></font>

This bot relies on the `CensysAPI` and aims to perform some common requests about hosts listed on Censys.

```python
with CensysBot(api_id, api_secret) as bot:
    result = bot.hosts_from_file(ips_path)
```

<font size="4"><b>`GhostProjectBot`</b></font>

<font size="4"><b>`HaveIBeenPwnedBot`</b></font>

<font size="4"><b>`HaveIBeenSoldBot`</b></font>

<font size="4"><b>`NuclearLeaksBot`</b></font>

<font size="4"><b>`ShodanBot`</b></font>

## CTF bots

<font size="4"><b>`RingZer0Bot`</b></font>

This bot realizes, using the `HTTPBot` class, the following steps for communicating with the related CTF website:

While entering bot's context:

- Set the given cookie for further communications
- Get the challenge page based on the input `cid` (Challenge ID)
- Parse the challenge page for the CSRF token
- Parse the challenge page for challenge inputs (attached in the `inputs` attribute as a dictionary)
- Execute bot's logics defined by the user (the `answer` attribute must be set at the end of the computation

While exiting the context:

- Submit user's answer and get the related response (where the flag is displayed)
- Parse the response for getting the flag
- Submit the flag for earning the points

```python
with RingZer0Bot(1, "session_cookie") as bot:
    # this binds relevant inputs for challenge #1
    # process bot.inputs
    # set the 'answer' attribute
```

<font size="4"><b>`RootMeIRCBot`</b></font>

This bot realizes, using the `IRCBot` class, the following steps for communicating with the related CTF website:

While initializing:

- Connect to `irc.root-me.org` on channel `#root-me_challenge` using the input nickname

While entering bot's context:

- Read data on the IRC channel up to a server-related pattern
- Send a server-formatted private message to Candy bot for getting the challenge input
- Parse the challenge input for making the `inputs` attribute

While leaving the context:

- Send a server-formatted private message to Candy bot with the challenge answer
- Read Candy bot's response for getting the flag and display it

```python
with RootMeIRCBot(1, "my_rootme_username") as bot:
    # this binds relevant inputs for challenge #1 in bot.inputs['message']
    # process bot.inputs['message']
    # set the 'answer' attribute
```

