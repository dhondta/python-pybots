**Disclaimer**: The following examples are simple challenges from Root-Me shown for the purpose of illustrating the use of `pybots`. As this website holds permanent challenges, the full solutions and resulting flags are not given.


## [Go back to college](https://www.root-me.org/en/Challenges/Programming/Go-back-to-college-147)

```python
import math
from pybots import RootMeIRCBot

with RootMeIRCBot(1, "your_pseudo") as bot:
    # INPUTS: the message from RootMe's IRC bot is in bot.inputs['message']
    # << write your logic here for computing the response >>
    bot.answer = ...  # assign computed result as answer to RootMe IRC bot
```

    12:34:56 [INFO] *flag*


-----


## [Uncompress me](https://www.root-me.org/en/Challenges/Programming/Uncompress-me)

```python
import base64
import zlib
from pybots import RootMeIRCBot

with RootMeIRCBot(4, "your_pseudo") as bot:
    # INPUTS: the message from RootMe's IRC bot is in bot.inputs['message']
    # << write your logic here for computing the response >>
    bot.answer = ...  # assign computed result as answer to RootMe IRC bot
```

    12:34:56 [INFO] *flag*
