## [Day 6 – Santa's journey](https://hackvent.hacking-lab.com?day=6)

*Follow Santa Claus as he makes his journey around the world.*

http://challenges.hackvent.hacking-lab.com:4200/

<font size="4"><b>1. Analysis</b></font>

Visiting the link provides a QRCode that can be easilly decoded with an online tool, providing the name of a country.

Refreshing the link provides another QRCode which corresponds to another country, and so forth.

<font size="4"><b>2. Solution</b></font>

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

url = "http://challenges.hackvent.hacking-lab.com:4200/"
with Hackvent2017_Day06(url) as bot:
    while not bot.next().data.startswith("HV17-"):
        continue
    print(bot.data)
```

    HV17-eCFw-J4xX-buy3-8pzG-kd3M


-----

## [Day 10 – Just play the game](https://hackvent.hacking-lab.com/challenge.php?day=10)

*Santa is in trouble. He's elves are busy playing TicTacToe. Beat them and help Sata to save christmas!*

```
nc challenges.hackvent.hacking-lab.com 1037
```

<font size="4"><b>1. Analysis</b></font>

By execute NetCat, one can play a simple TicTacToe game that indicates, upon winning, that 100 games must be won to get the flag.

The goal is thus to find the winning sequences and to program a bot so that it can solve the challenge in an automated way.

<font size="4"><b>2. Solution</b></font>

By trial-and-error, one can determine the following sequences, formatted as nested lists of the type:

```
[
    local bot play,
    dictionary with:
        key: remote bot play
        value: nested list with [local bot play, ...]
]
```


```python
moves = [1, {
    2: [7, {
        3: 4,
        0: [5, {
            3: 9,
            0: 3,
        }],
    }],
    4: [3, {
        0: [5, {
            3: 9,
            0: 7,
        }],
    }],
    5: [9, {
        2: [8, {
            3: 7,
            7: [3, {
                4: 6,
                6: 4,
            }] ,
        }],
        3: [7, {
            8: 4,
            4: 8,
            }],
        0: 8,
    }],
}]
```

The following NetCat bot then solves the challenge by using the patterns found in the traces got by trial-and-error.


```python
from pybots.netcat import Netcat

FLAG = re.compile(r'HV17(\-[a-z0-9]{4}){5}', re.I)

class Hackvent2017_Day10(Netcat):
    first_play = True
    game_count = 0
    patterns = {
        'first': "Press enter to start the game",
        'new': "Press enter to start again",
        'play': "Field:",
        'won': "Congratulations you won! 100/100",
    }
    max_games = 200
    won = False
    
    def _bot_play(self):
        transform = lambda l: map(lambda x: x.strip(),
                                  filter(lambda x: x != '',
                                         ''.join(l).split("|")))
        self.trace = filter(lambda x: x.startswith("|") and x.endswith("|"),
                            map(lambda x: x.strip(), self.trace.split('\n')))
        self.trace = [self.trace[i:i+3] for i in range(0, len(self.trace), 3)]
        if len(self.trace) > 1:
            l = [None if j[0] == j[1] else i for i, j in \
                 enumerate(zip(*map(transform, self.trace)))]
            return filter(lambda x: x is not None, l)[0] + 1
    
    def play(self, l):
        self.write(str(l[0]))
        self.trace = self.read_until(self.patterns['play'])
        try:
            index = self._bot_play()
            next_move = l[1][index]
            if isinstance(next_move, list):
                self.play(next_move)
            else:
                self.write(str(next_move))
        except KeyError:
            next_move = l[1][0]
            if isinstance(next_move, list):
                self.play(next_move)
            else:
                self.write(str(next_move))
        
    def win(self):
        data = self.read_until(self.patterns['first'] \
                    if self.first_play  else self.patterns['new'])
        self.first_play = False
        self.write("")
        self.read_until(self.patterns['play'])
        self.play(moves)
        self.game_count += 1
        if self.patterns['won'] in data:
            self.won = True
            print(FLAG.search(data).group())

with Hackvent2017_Day10("challenges.hackvent.hacking-lab.com", 1037) as nc:
    while not nc.won and nc.game_count < nc.max_games:
        nc.win()
```

    HV17-y0ue-kn0w-7h4t-g4me-sure
