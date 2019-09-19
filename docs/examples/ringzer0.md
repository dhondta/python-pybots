**Disclaimer**: The following examples are simple challenges from RingZer0 shown for the purpose of illustrating the use of `pybots`. As this website holds permanent challenges, the full solutions and resulting flags are not given.


## [13 – Hash me if you can](https://ringzer0team.com/challenges/13)

```python
import hashlib
from pybots import RingZer0Bot

with RingZer0Bot(13, cookie="your_session_cookie") as bot:
    # INPUTS: the message from the Web page is in bot.inputs['MESSAGE']
    # << write your logic here for computing the hash >>
    bot.answer = ...  # assign computed hash as answer to the CTF website
    # NB: the flag will be immediately submitted for earning the points
```

```sh
12:34:56 [INFO] Challenge information:
12:34:56 [INFO]  - Title    : Hash me if you can
12:34:56 [INFO]  - Statement: You have 2 seconds to hash this message using
sha512 algorithm
12:34:57 [INFO] Flag found: ...
```

-----


## [17 – Read me if you can](https://ringzer0team.com/challenges/17)

```python
import pytesseract
from PIL import Image
from pybots import RingZer0Bot

with RingZer0Bot(17, cookie="your_session_cookie") as bot:
    # INPUTS: the image from the Web page is in bot.inputs['IMAGE']
    # << write your logic here for handling the image >>
    bot.answer = ...  # assign converted image as a string using pytesseract
    # NB: the flag will be immediately submitted for earning the points
```

```sh
12:34:56 [INFO] Challenge information:
12:34:56 [INFO]  - Title    : Read me if you can
12:34:56 [INFO]  - Statement: You have 2 seconds to parse the word.
12:34:58 [INFO] Flag found: ...
```
