Can you spare me a dollar?
==========================

:dollar: A simple script asking all of your Venmo friends a dollar :dollar:

Usage
-----

### Basic
```
$ git clone https://github.com/jaewoongh/can-you-spare-me-a-dollar.git
$ cd can-you-spare-me-a-dollar/
$ ./can-you-spare-me-a-dollar.rb -t YOUR_TOKEN_HERE
```

### Options
```
Usage: ./can-you-spare-me-a-dollar.rb
       [-t <access_token>] [-n <message>] [-c <amount>]
       [-a <public|friends|private>] [-d <number>] [-l <number>]
       [-F] [-v]
  -t, --token (REQUIRED)  Venmo developer access token
  -n, --note              Note for the transaction
  -c, --charge            Amount to charge; minus value for payment
  -a, --audience          Sharing setting for the transaction
  -d, --depth             If specified, get friends' friends' friends..
  -l, --limit             Limit charging request not to exceed this number
  -F, --no-friends        Don't charge your direct friends
  -v, --verbose           Be verbose
```
```
*Default note:       "Can you spare me a dollar?"  
*Default charge:     A dollar  
*Default audience:   According to your Venmo settings  
*Default depth:      1  
*Default limit:      None  
*Default no-friends: false  
*Default verbose:    false
```

Get friends' friends, but exclude direct friends. Be verbose. Ask 500 friends at most:
```
./can-you-spare-me-a-dollar.rb -vFd 2 -l 500 -t YOUR_TOKEN_HERE
```
*Giving depth a value more than 1 may result in crazy number of people, even with only 2.

Getting your access token
-------------------------
Go to Venmo website for account settings, [developers tab](https://venmo.com/account/settings/developers).  
There you can see your Access Token.  
Don't ever let others know your token!

Disclaimer
----------
If someone could get your access token, he can do anything with your account.  
So keep it as your own, and use this at your own risk.  
It's just using Venmo API, nothing's bad or dangerous though.

Also, please take your own risk for massive requests.  
It's apparently not a desirable usage of the API when you do that.

Where this came from
-----------------------
This project is done as a weekly assignment for the class Appropriating Interaction Technoligies by Kyle McDonald and Lauren McCarthy @ITP, Tisch School of the Arts, NYU.

```
Creatively misuse an existing API in order to reveal something about the service.
```

Ruby vs. Python
---------------
Originally written in python, but both scripts do the exact same thing.  
If you use python script instead of ruby one though, you'll need [requests](http://docs.python-requests.org/en/latest/user/install/) module for python.