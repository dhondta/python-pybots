## <img src="https://sigterm.ch/wp-content/uploads/2017/04/challenge_22-300x188.jpg" alt="" width="20%"/> [22 – Game, Set and Hash](https://hackyeaster.hacking-lab.com/hackyeaster/challenge22.html)

*Can you beat the tennis master?*

```
hackyeaster.hacking-lab.com:8888
```

<font size="4"><b>Short Solution</b></font>

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


<font size="4"><b>Solution Explained</b></font>

<font size="4"><b>1. Analysis</b></font>

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

<font size="4"><b>2. Solution</b></font>

<font size="3"><b>2.1 Finding the right wordlist</b></font>

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


<font size="3"><b>2.2 Automating the game with a Netcat bot</b></font>

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


-----

## <img src="https://sigterm.ch/wp-content/uploads/2017/04/challenge_24-300x188.jpg" alt="" width="20%"/> [24 – Your Passport, please](https://hackyeaster.hacking-lab.com/hackyeaster/challenge24.html)

*After another exhausting Easter, Thumper decides to travel abroad for recreation. As a real h4x0r, he of course is using his own, homemade e-passport:*

<img src="https://sigterm.ch/wp-content/uploads/2017/04/hacky_epass-300x208.png"/>

*Write a client which connects to the virtual terminal, and fetch the portrait photo stored on Thumper's passport! The virtual terminal is running on:*

```
hackyeaster.hacking-lab.com:7777
```

*As a starting point for your client, the following eclipse project is provided:*

**File**: [`epassclient.zip`](https://sigterm.ch/stuff/hackyeaster17/24_epassclient.zip)

<font size="4"><b>Short Solution</b></font>

```python
from pybots.epassport import EPassport

with EPassport('hackyeaster.hacking-lab.com', 7777) as p:
    p.set_MRZ("P012345673HLA7707076M21010150000007<<<<<<<96").get_photo("hacky-easter-2017-24/egg.jpg")
```

<font size="4"><b>Solution Explained</b></font>

<font size="4"><b>1. Analysis</b></font>

First, by opening the provided project archive, one can figure out that the source code is located at `epassclient/src/ch/he17/epassclient/` and structured as follows:
- `JMRTDMain.java`: the virtual terminal server application
- `terminal/HE17Card.java`: the card representation (with a hard-coded ATR) based on `smartcardio` package's card definition
- `terminal/HE17Channel.java`: the channel for transmitting and receiving data using APDU classes from `smartcardio` package
- `terminal/HE17Terminal.java`: the virtual terminal that connects to the remote host and manages the presense of the card

As the complete protocol is missing in `JMRTDMain.java`, one needs to find a way to communicate with the remote virtual terminal. For this purpose, it is of common knowledge that epassports follow the [ICAO Doc 9303 standard](https://www.icao.int/publications/pages/publication.aspx?docnum=9303).

According to the Doc9303 specification, the Logical Data Structre (LDS) is defined as follows:

<img src="https://i.stack.imgur.com/LZZAp.png"/>

In this structure, one can see that the portrait photo is located at the Data Group 2 (DG2), that is, *Encoded Face*. On this photo, there should be the classical QR Code required to win the challenge.

**Goals**:
1. Implement the protocol required to connect to the virtual terminal
2. Retrieve the content of DG2

**Notes**:
- The ATR (Answer To Reset) can be checked on [Smart Card ATR Parsing](https://smartcard-atr.appspot.com/parse?ATR=3B8880010073C8400000900062) using the bytes found in `epassclient.zip/src/ch/he17/epassclient/terminal/HE17Card.java`.
- Also in the same file, one can see that the defined protocol is `T=1`.

**Acronyms**:
- APDU: Application Protocol Data Unit
- BAC: Basic Access Control
- MRTD: Machine Readable Travel Document
- MRZ: Machine Readable Zone

<font size="4"><b>2. Solution</b></font>

<font size="3"><b>2.1 Creating a communication bot</b></font>

First, let's define a bot for communicating with the remote virtual terminal.


```python
from pybots.netcat import Netcat

with Netcat('hackyeaster.hacking-lab.com', 7777) as nc:
    print(nc.read_until('\n', disp=True))
    # do nothing yet ; just retrieve what the server tells while starting the communication
```

    Passport reader terminal. Card presented... send your apdus as hex-strings terminated by newline



The terminal asks for APDU's, as it was expected because of the protocol required to read the epassport.

<font size="3"><b>2.2 Handling the exchange protocol</b></font>

So, the question is now to figure out which APDU's are required. First, using [the standard (Doc 9303 Specification - Part 10)](https://www.icao.int/publications/Documents/9303_p10_cons_en.pdf), let's inspect the structure of an APDU:

- Command

    ```
     1B   1B   1B  1B  1B   7B   1B
    [CLA][INS][P1][P2][Lc][Data][Le]
    ```
    - `CLA`: instruction class
    - `INS`: instruction type
    - `P1/P2`: additional instruction parameters (e.g. file identifier, file offset)
    - `Lc`: length of input data
    - `Data`: input data
    - `Le`: length of expected output data


- Response

    ```
           2B
    [0x9000|0x6C14]
    ```
    - `0x9000`: everything is OK
    - `0x6C14`: 20 output bytes are ready

There now remains to find how to use the APDU's, that is, the protocol.

For this purpose, one can rely on [this technical guideline](https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/Publications/TechGuidelines/TR03110/BSI_TR-03110_Part-1_V2-2.pdf?__blob=publicationFile) from which the following steps can be deduced:

1. Select Application
2. Perform BAC (based on MRZ)
3. Read DG2

The first step is simple ; it is about sending a *Command APDU* that selects the `eMRTD Application` for reading DG2 afterwards. This is done with the following APDU (see [standard (Doc 9303 Specification - Part 10)](hacky-easter-2017-24/ePassport-doc9303_part10_en.pdf) at pages 8 and 12):
- `CLA  = 00`
- `INS  = A4`
- `P1   = 04`
- `P2   = 0C`
- `Lc   = 07` (computed because of the Application ID `AID`)
- `Data = A0000002471001` (that is, the `AID` of `eMRTD Application`)

Which gives, in term of valid input for the remote virtual terminal:

```
00A4040C07A0000002471001
```

Testing this input gives `9000` as a reponse, which shows that it works as this is the *Response APDU* that tells that everything is OK. This then shows the output format when the remort virtual terminal answers.

In order to simplify working with the standard, let's try to work with a Python library that already implements it. For this purpose, one can find [`pypassport-2.0`](https://github.com/andrew867/epassportviewer/tree/master/pypassport-2.0/), which is part of the [`epassportviewer` project](https://github.com/andrew867/epassportviewer).

<font size="3"><b>2.3 Using `pypassport-2.0`</b></font>

After manual install, one can find help in the `pypassport.epassport` module that provides an interesting example.


```python
import pypassport.epassport
#help(pypassport.epassport)
```

```
     |  >>> from pypassport.epassport import EPassport, mrz
     |  >>> from pypassport.reader import pcscAutoDetect
     |  >>> from pypassport.openssl import OpenSSLException
     |  >>> detect = pcscAutoDetect()
     |  >>> detect
     |  (<pypassport.reader.pcscReader object at 0x00CA46F0>, 1, 'OMNIKEY CardMan 5x21-CL 0', 'GENERIC')
     |  >>> reader = detect[0]
     |  >>> mrz = mrz.MRZ('EHxxxxxx<0BELxxxxxx8Mxxxxxx7<<<<<<<<<<<<<<04')
     |  >>> mrz.checkMRZ()
     |  True
     |  >>> p = EPassport(mrz, reader)
     |  Select Passport Application
     |  >>> p["DG1"]
     |  Reading DG1
```

In order to use this library, one needs to create a reader that handles the challenge-related virtual terminal. This will allow use to read DG2 without caring for implementing the aforementioned steps.

Let's thus emulate it implementing the required methods from the `Reader` template class. The customized reader will simply bind an input bot for dealing with the remote virtual terminal.

```python
from pypassport.apdu import ResponseAPDU
from pypassport.reader import Reader

class RemoteVirtualTerminal(Reader):
    readerNum = 0
    
    def __init__(self, bot):
        self.__bot = bot
    
    def __write(self, apdu):
        self.__bot.write("".join(x.strip(">[]") for x in str(apdu).split()))
        
    def connect(self, readerNum=None):
        pass  # no need to connect as this is handled in the bot
    
    def disconnect(self):
        pass  # no need to disconnect as this is handled in the bot
    
    def getReaderList(self):
        return ["WebTerminal"]
    
    def transmit(self, apdu):
        print("--{}".format(str(apdu)))
        self.__write(apdu)
        response = self.__bot.read_until('\n').rstrip()
        response, code = response[:-4], response[-4:]
        shortened = (response[:37] + '...') if len(response) > 40 else response
        intcode = [int('0x{}'.format(h), 16) for h in re.findall('..', code)]
        print("<-- {} ({})".format("{} [{}]".format(shortened, code).strip(),
                                 ["Error", "OK"][code == "9000"]))
        return ResponseAPDU(response.decode('hex'), *intcode)
```

There now remains to instantiate the reader using the dedicated EPassport bot implemented in the `pybots` library with MRZ's relavant information (that is, the second line, with the *Document Number*, the *Date of Birth* and the *Date of Expiracy*, required for the BAC).

<font size="3"><b>2.4 Solving the challenge with `pybots`</b></font>

```python
from pybots.epassport import EPassport

with EPassport('hackyeaster.hacking-lab.com', 7777, verbose=True) as p:
    p.set_MRZ("P012345673HLA7707076M21010150000007<<<<<<<96").get_photo("photo.jpg")
```

    20:49:29 [DEBUG] Initialization done.
    20:49:29 [DEBUG] Precomputing...
    20:49:29 [DEBUG] Precomputation done.
    20:49:29 [DEBUG] Processing preamble...
    20:49:29 [DEBUG] Preamble done.
    20:49:29 [INFO] Select eMRTD Application
    20:49:29 [DEBUG] --> 00 A4 04 0C 07 [A0000002471001] 
    20:49:30 [DEBUG] <-- [9000]
    20:49:30 [DEBUG] Ingoing APDU format determined as hex string
    20:49:30 [DEBUG] Outgoing APDU format determined as hex string
    20:49:30 [DEBUG] --> 00 A4 04 0C 07 [A0000002471001] 
    20:49:30 [DEBUG] <-- [9000]
    20:49:30 [INFO] Basic Access Control
    20:49:30 [DEBUG] --> 00 84 00 00  [] 08
    20:49:30 [DEBUG] <-- 6C5544797A91115D [9000]
    20:49:30 [DEBUG] --> 00 82 00 00 28 [61EFAA9CD7DC1339180F94C0122289D424650E69CFF61A7DCA77B8AD4E84E463D659B8E3EC71B4B3] 28
    20:49:30 [DEBUG] <-- B54E73D9D815F466A4310CE62496E1BA595EB... [9000]
    20:49:30 [INFO] Get encoded face from DG2
    20:49:30 [DEBUG] --> 0C A4 02 0C 15 [8709014EC2A66E1EC4B6EC8E08C32FB3DF944BA521] 00

    Passport reader terminal. Card presented... send your apdus as hex-strings terminated by newline

    20:49:30 [DEBUG] <-- 990290008E083616DFFCE923C223 [9000]
    20:49:30 [DEBUG] --> 0C B0 00 00 0D [9701048E088B8BABCF9D23EA51] 00
    20:49:30 [DEBUG] <-- 870901D2CDEE703212A0C0990290008E08923... [9000]
    20:49:30 [DEBUG] --> 0C B0 00 04 0D [9701DF8E0830AFA9A3F8309722] 00
    20:49:30 [DEBUG] <-- 8781E1017E3391D06B2A8A52E206B8A62A099... [9000]
    [...]
    20:49:32 [DEBUG] --> 0C B0 2F 0E 0D [9701DF8E08ABEC4B23520EA036] 00
    20:49:32 [DEBUG] <-- 8781E101745279A1C3F735EE6D7AE218C41CA... [9000]
    20:49:32 [DEBUG] --> 0C B0 2F ED 0D [9701DF8E08569542EB4BD3E56A] 00
    20:49:32 [DEBUG] <-- 8781E101D0F17D2E3F7835BAB9F999AED6C84... [9000]
    20:49:32 [DEBUG] --> 0C B0 30 CC 0D [9701688E08F73FED88C49A5CBF] 00
    20:49:32 [DEBUG] <-- 8771012E7234DF8E7C46F46DBA03786BC7DFE... [9000]
