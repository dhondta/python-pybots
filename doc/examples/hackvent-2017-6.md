# Day 06: Santa's journey

###### Make sure Santa visits every country

<div class="metadata-table"></div>

**Category** | **Keywords** | **Tools** | **Reference**
--- | --- | --- | ---
General | Santa, journey, tracker | `pybots` | [Hackvent 2017](https://hackvent.hacking-lab.com?day=6)

*Follow Santa Claus as he makes his journey around the world.*

http://challenges.hackvent.hacking-lab.com:4200/

## 1. Analysis

Visiting the link provides a QRCode that can be easilly decoded with an online tool, providing the name of a country.

Refreshing the link provides another QRCode which corresponds to another country, and so forth.

## 2. Solution

Let's code a bot that will request QRCodes and decode them until it matches a valid flag.


```python
from qrtools import QR
from pybots.http import HTTPBot

class Hackvent2017_Day06(HTTPBot):
    qr = QR()
    tmp_file = "/tmp/qrcode.png"
    
    def next(self):
        self.get()
        with open(self.tmp_file, 'wb') as f:
            for chunk in self.response:
                f.write(chunk)
        self.qr.decode(self.tmp_file)
        self.data = self.qr.data
        return self

with Hackvent2017_Day06("http://challenges.hackvent.hacking-lab.com:4200/") as bot:
    while not bot.next().data.startswith("HV17-"):
        continue
    print(bot.data)
```

    HV17-eCFw-J4xX-buy3-8pzG-kd3M
