#!/usr/bin/env python

import random
import requests

user_id = random.randint(1300000000000000000, 1600000000000000000)
print user_id
stranger = requests.get('https://api.venmo.com/v1/users/' + str(user_id) + '?access_token=KARtLK2YAdgaA9tKV6naPXw7hay8Xxnk').json()
print stranger