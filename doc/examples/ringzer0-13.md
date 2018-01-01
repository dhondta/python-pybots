# Hash me if you can

<div class="metadata-table"></div>

**Category** | **Keywords** | **Tools** | **Reference**
--- | --- | --- | ---
Coding | SHA512 | `pybots` | [RingZer0](https://ringzer0team.com/challenges/13)

### Solving the challenge with `pybots`

```python
from pybots.ctf.ringzero import RingZer0Bot

with RingZer0Bot(13, cookie="your_session_cookie") as bot:
    # INPUTS: the message from the Web page is in bot.inputs['MESSAGE']
    # << write your logic here for computing the hash >>
    bot.answer = ...  # assign the computed hash as bot's answer to the CTF website
    # NB: the flag will be immediately submitted for earning the points
```

    12:34:56 [INFO] Challenge information:
    12:34:56 [INFO]  - Title    : Hash me if you can
    12:34:56 [INFO]  - Statement: You have 2 seconds to hash this message using sha512 algorithm
    12:34:57 [INFO] Flag found: ...
