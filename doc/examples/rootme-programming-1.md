# Go back to college

<div class="metadata-table"></div>

**Category** | **Keywords** | **Tools** | **Reference**
--- | --- | --- | ---
Programming |  | `pybots` | [Root-Me](https://www.root-me.org/en/Challenges/Programming/Go-back-to-college-147)

### Solving the challenge with `pybots`

```python
import math
from pybots.ctf.rootme import RootMeIRCBot

with RootMeIRCBot(1, "your_pseudo") as bot:
    # INPUTS: the message from RootMe's IRC bot is in bot.inputs['message']
    # << write your logic here for computing the response >>
    bot.answer = ...  # assign the computed result as bot's answer to RootMe's IRC bot
```

    12:34:56 [INFO] *flag*
