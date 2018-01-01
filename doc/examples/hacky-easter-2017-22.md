# Game, Set and Hash

<div class="metadata-table"></div>

<table>
<tr>
<td rowspan="2" width="20%"><img src="hacky-easter-2017-22/challenge.jpg"/></td>
<th height="20px"><b>Category</b></th>
<th><b>Keywords</b></th>
<th><b>Tools</b></th>
<th><b>Reference</b></th>
</tr>
<tr>
<td>Programming</td>
<td>Tennis, SHA256, Netcat</td>
<td>
Netcat, <code>pybots</code>
</td>
<td><a href="https://hackyeaster.hacking-lab.com/hackyeaster/challenge22.html">Hacky Easter 2017</a></td>
</tr>
</table>

*Can you beat the tennis master?*

```
hackyeaster.hacking-lab.com:8888
```

# Short Solution

```python
from pybots.netcat import Netcat

class TennisSuperMaster(Netcat):
    def precompute(self):
        self.lookup = LookupTable("/home/morfal/.dict/realhuman_phill.txt",
                                  algorithm="sha256",
                                  dict_filter=lambda x: x.islower() and x.isalnum())
        
with TennisSuperMaster("hackyeaster.hacking-lab.com", 8888) as nc:
    nc.read_until("?")
    nc.write("y")
    nc.read()
    message, answer = "Not started", " :-/"
    print("Playing...")
    while True:
        message = nc.read()
        if "You lose!" in message or "You win!" in message:
            print(message)
            break
        data, plain = message.split("-" * 22)[-1].strip(), ""
        if re.match(r'^[a-f0-9]{64}$', data):
            plain = nc.lookup.get(data)
        nc.write(plain)
        nc.read()
```


# Solution Explained

## 1. Analysis

First let's connect with Netcat and check what it is about.

```session
$ nc hackyeaster.hacking-lab.com 8888
Ready for the game?
y
Let's go!
623210167553939c87ed8c5f2bfe0b3e0684e12c3a3dd2513613c4e67263b5a1
test
Wrong! Point for me.
----------------------
Player > 0 0
Master   0 15
----------------------
e11d8cb94b54e0a2fd0e780f93dd51837fd39bf0c9b86f21e760d02a8550ddf7
Timeout. You loose!
```

This "tennis" game seems to work by sending a hash and the correct corresponding value must be returned to get points.

**Important Note**: The game holds a timeout of around 10 seconds, which means that performing a request on a hash craking website or cracking each hash with John The Ripper would not allow to win the game.

## 2. Solution

### 2.1 Finding the right wordlist

Let's then first get some hashes and try to crack them with [Crackstation.net](https://crackstation.net/):

```
3beb460e56ea841b9eb9fd8a297fa680562e9a1d33df7540479c2ed037ab4883    sha256  tobias
2fe70f8fab887c96dd0abb620572088ea2a5435ef9fe82d635b553af88e55896    sha256  gabriela
b0e18c0332f39c44531d5bc1e09a47936e07a284ecaf4ef3ef92aa1fd4af9876    sha256  jordan1
19a517a5258e9b02ddce1a03a44b9d76251cc331aaa41c1b1e12bffc8a7fc32f    sha256  myspace1
74dd730b5c36c1cb4fdbb4bce1764c57f260190f94ba52d877308332f1dfe363    sha256  turtle
59945da25d2521045b4bc84db7d5fd44b2c5511fe7cc247a8ce5a79bcd74a1c2    sha256  football1
4748d4c802a775e8db9a23ec58f0986cacdc5d2d3356d22c490a7d22331ff133    sha256  walter
e647708a52060743eb1dc963732cfedc1ea1db3a1785da3fb9c50dd3954fd708    sha256  barcelona
10426253a2fcb6db8c40fd0376c95b791bae0973258facd7421e6d9be87e8dc6    sha256  fatassa121690
6d26902e4a604f52162563a463a0f7c077f73535d5e3a1464444534b07c16745    sha256  badjao19
```

Interestingly all of the given hashes could be cracked. This may mean that using a wordlist of [Crackstation.net](https://crackstation.net/) could be a good choice. Let's choose the [*Smaller Wordlist (Human Passwords Only)*](https://crackstation.net/files/crackstation-human-only.txt.gz) that will be filtered for smaller memory use with a Netcat bot.


### 2.2 Automating the game with a Netcat bot

Now that we know which wordlist to use, we can prepare a bot for automatically communicating with the server. This will precompute the lookup table and then open a connection with the server in order to win the game.

From the previous observations while trying by hand, one can point out that:
- **Wordlist filter**: lowercase, alphanumeric
- **Preambule**: recv("?") -> send("y") -> recv()
- **Round**: recv("...[hash]") -> lookup(hash) -> send(plaintext) -> recv([answer, score])
- **End condition**: string "`You lose!`", thus surely also "`You win!`"


```python
class LookupTable(object):
    """
    Lookup table class for password cracking.

    :param dictionary: the dictionary file to be loaded
    :param algorithm: the hash algorithm to be used
    :param ratio: ratio of value to be hashed in the lookup table (by default,
                    every value is considered but, i.e. with a big wordlist, it
                    can be better to use a ratio of 2/3/4/5/... in order to
                    limit the memory load)
    """
    def __init__(self, dictionary, algorithm="md5", ratio=1, dict_filter=None,
                 verbose=True):
        assert os.path.isfile(dictionary)
        assert algorithm in ["md5", "sha1", "sha256"]
        assert isinstance(ratio, int) and ratio > 0
        algorithm = eval(algorithm)
        self.__lookup = {}
        if verbose:
            print("Making the lookup table ; this may take a while...")
        with open(dictionary) as f:
            for i, l in enumerate(f):
                if i % ratio == 0:
                    l = l.strip()
                    if hasattr(dict_filter, '__call__') and dict_filter(l):
                        self.__lookup[algorithm(l)] = l
        if verbose:
            print("Lookup table ready!")

    def get(self, h):
        """
        Cracking public method

        :param h: input hash
        :return: corresponding value
        """
        try:
            return self.__lookup[h]
        except KeyError:
            return ""
```

```python
from pybots.netcat import Netcat

class TennisSuperMaster(Netcat):
    def precompute(self):
        self.lookup = LookupTable("/home/morfal/.dict/realhuman_phill.txt",
                                  algorithm="sha256",
                                  dict_filter=lambda x: x.islower() and x.isalnum())
        
with TennisSuperMaster("hackyeaster.hacking-lab.com", 8888) as nc:
    nc.read_until("?")
    nc.write("y")
    nc.read()
    message, answer = "Not started", " :-/"
    print("Playing...")
    while True:
        message = nc.read()
        if "You lose!" in message or "You win!" in message:
            print(message)
            break
        data, plain = message.split("-" * 22)[-1].strip(), ""
        if re.match(r'^[a-f0-9]{64}$', data):
            plain = nc.lookup.get(data)
        nc.write(plain)
        nc.read()
```

    Making the lookup table ; this may take a while...
    Lookup table ready!
    Playing...
    ----------------------
    Player > 6 6 6 
    Master   0 0 0 
    ----------------------
    You win! Solution is: !stan-the_marth0n$m4n


**Sample trace**: [`trace.txt`](hacky-easter-2017-22/trace.txt)

**Egg**:  <img src="hacky-easter-2017-22/egg.png" width="10%">
