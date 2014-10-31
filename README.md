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
Usage: ./can-you-spare-me-a-dollar.rb [-t <access_token>] [-n <message>] [-c <amount>] [-a <public|friends|private>]'

  -t, --token (REQUIRED)  Venmo developer access token
  -n, --note              Note for the transaction
  -c, --charge            Amount to charge? Minus value for payment
  -a, --audience          Sharing setting for the transaction
```

*Default note: "Can you spare me a dollar?"  
*Default charge: A dollar  
*Default audience: According to your Venmo settings  

Getting your access token
-------------------------
Go to Venmo website for account settings, [developers tab](https://venmo.com/account/settings/developers).  
There you can see your Access Token.  
Don't ever let others know your token!

Dependencies
------------
I believe you need to install [ruby](https://www.ruby-lang.org/en/downloads/).

Disclaimer
----------
If someone could get your access token, he can do anything with your account.  
So keep it as your own, and use this at your own risk.  
It's just using Venmo API, nothing's bad or dangerous though.

Was thinking of making this as a web service, but I didn't want anybody submit his access token online.

Where this came from
-----------------------
This project is done as a weekly assignment for the class Appropriating Interaction Technoligies by Kyle McDonald and Lauren McCarthy @ITP, Tisch School of the Arts, NYU.

```
Creatively misuse an existing API in order to reveal something about the service.
```

It'd be really awesome and dangerous if I could actually grab some random strangers' Venmo ID and ask them a dollar.

One last note
-------------
Originally written in python, but for independency regarding http requests, I've rewrote the code in ruby.  
Both scripts do the exact same thing, but you need `requests` module for python version.