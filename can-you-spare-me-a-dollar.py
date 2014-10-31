#!/usr/bin/env python

import sys
from sys import argv
import getopt

import requests


# Usage manual
def usage(message):
	if message is not None:
		print message
		print
	print 'Usage: ./can-you-spare-me-a-dollar.py [-t <access_token>] [-n <message>] [-c <amount>] [-a <public|friends|private>]'
	print
	print '  -t, --token (REQUIRED)  Venmo developer access token'
	print '  -n, --note              Note for the transaction'
	print '  -c, --charge            Amount to charge; minus value for payment'
	print '  -a, --audience          Sharing setting for the transaction'
	return

# Get command line options and arguments
access_token = None
note = 'Can you spare me a dollar?'
charge_amount = -1
audience = None
try:
	opts, args = getopt.getopt(argv[1:], 't:n:c:a:', ['token=', 'note=', 'charge=', 'audience='])
except getopt.GetoptError:
	usage(None)
	sys.exit(2)

# Handle API error response
def handle_error(e):
	print e['message'] + ' (' + str(e['code']) + ')'
	sys.exit(2)

# Check if those options are valid
for opt, val in opts:
	if opt == '-t':
		access_token = val
	elif opt == '-n':
		note = val
	elif opt == '-c':
		charge_amount = -val
	elif opt == '-a':
		if val.lower() in ('public', 'friends', 'private'):
			audience = val.lower()
		else:
			usage('Audience can be public, friends, or private')
			sys.exit(2)

if access_token is None:
	usage('You must give an access token!')
	sys.exit(2)

# Get my id
me = requests.get('https://api.venmo.com/v1/me?access_token=' + access_token).json()
try:
	handle_error(me['error'])
except KeyError:
	pass
id_mine = me['data']['user']['id']

# Get friends' id
def get_friends(req):
	friends_got = requests.get(req + '&access_token=' + access_token).json()
	try:
		handle_error(friends_got['error'])
	except KeyError:
		pass
	friends = friends_got['data']
	return {'next': friends_got['pagination']['next'], 'ids': [f['id'] for f in friends]}

a_page_of_friends = get_friends('https://api.venmo.com/v1/users/' + id_mine + '/friends?limit=50')
id_friends = a_page_of_friends['ids']
while True:
	next_page = a_page_of_friends['next']
	if next_page is None:
		break
	else:
		a_page_of_friends = get_friends(next_page)
	id_friends += a_page_of_friends['ids']

# Charge everyone!
error_num = 0
error_list = list()
for id in id_friends:
	params = {'access_token': access_token, 'user_id': id, 'note': note, 'amount': charge_amount}
	if audience is not None:
		params['audience'] = audience
	result = requests.post('https://api.venmo.com/v1/payments', data=params).json()
	try:
		error_list.append(result['error'])
		error_num += 1
	except KeyError:
		pass

# Check results
if error_num > 0:
	print str(error_num) + ' error(s) occured during the process:'
	print
	for e in error_list:
		print e['message'] + ' (' + str(e['code']) + ')'
	print
	print 'Process finished with some errors (' + str(len(friends) - len(error_list)) + '/' + str(len(friends)) + ')'
else:
	print 'Charging successfully finished! (' + str(len(friends)) + ')'

print 'Note: ' + note
print 'Charge amount: ' + str(-charge_amount)
if audience is not None:
	print 'Audience: ' + audience