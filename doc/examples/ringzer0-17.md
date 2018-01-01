# Read me if you can

<div class="metadata-table"></div>

**Category** | **Keywords** | **Tools** | **Reference**
--- | --- | --- | ---
Coding | OCR, PIL, Tesseract | `pybots` | [RingZer0](https://ringzer0team.com/challenges/17)

### Solving the challenge with `pybots`

```python
import pytesseract
from PIL import Image
from pybots.ctf.ringzero import RingZer0Bot

with RingZer0Bot(17, cookie="your_session_cookie") as bot:
    # INPUTS: the image from the Web page is in bot.inputs['IMAGE']
    # << write your logic here for handling the image >>
    bot.answer = ...  # assign converted image as a string using pytesseract
    # NB: the flag will be immediately submitted for earning the points
```

    12:34:56 [INFO] Challenge information:
    12:34:56 [INFO]  - Title    : Read me if you can
    12:34:56 [INFO]  - Statement: You have 2 seconds to parse the word.
    12:34:58 [INFO] Flag found: ...
