#!/usr/bin/env python

import sys
from sys import argv
import getopt

from collections import Counter

import requests


# Usage manual
def usage(message):
	if message is not None:
		print message
		print
	print 'Usage: ./can-you-spare-me-a-dollar.py'
	print '       [-t <access_token>] [-n <message>] [-c <amount>]'
	print '       [-a <public|friends|private>] [-d <number>] [-l <number>]'
	print '       [-F] [-v]'
	print
	print '  -t, --token (REQUIRED)  Venmo developer access token'
	print '  -n, --note              Note for the transaction'
	print '  -c, --charge            Amount to charge; minus value for payment'
	print '  -a, --audience          Sharing setting for the transaction'
	print '  -d, --depth             If specified, get friends\' friends\' friends..'
	print '  -l, --limit             Limit charging request not to exceed this number'
	print '  -F, --no-friends        Don\'t charge your direct friends'
	print '  -v, --verbose           Be verbose'
	return

# Get command line options and arguments
access_token = None
note = 'Can you spare me a dollar?'
charge_amount = -1
audience = None
lookup_depth = 1
limit_request = None
no_friends = False
verbose = False
try:
	opts, args = getopt.getopt(argv[1:], 't:n:c:a:d:l:Fv', ['token=', 'note=', 'charge=', 'audience=', 'depth=', 'limit=', 'no-friends', 'verbose'])
except getopt.GetoptError:
	usage(None)
	sys.exit(2)

# Handle API error response
def handle_error(e):
	print
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
	elif opt == '-d':
		lookup_depth = int(val)
	elif opt == '-l':
		limit_request = int(val)
	elif opt == '-F':
		no_friends = True
	elif opt == '-v':
		verbose = True

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

# Function for getting a page of friends
def get_a_page_of_friends(req):
	friends_got = requests.get(req + '&access_token=' + access_token).json()
	try:
		handle_error(friends_got['error'])
	except KeyError:
		pass
	if verbose:
		for f in friends_got['data']:
			print f['display_name'] + ',',
	return friends_got

# Function for getting friends looking through many pages if neccessary
def get_friends(req):
	pages_of_friends = list()
	a_page_of_friends = get_a_page_of_friends(req)
	pages_of_friends = a_page_of_friends['data'][:]
	while True:
		next_page = a_page_of_friends['pagination']['next']
		if next_page is None:
			break
		else:
			a_page_of_friends = get_a_page_of_friends(next_page)
			pages_of_friends += a_page_of_friends['data'][:]
	return pages_of_friends

# Function to remove duplicates in a list of dicts
def remove_duplicates(l):
	return [dict(tupleized) for tupleized in set(tuple(item.items()) for item in l)]

# Function for getting friends over and over to desired depth
def get_a_depth_of_friends(fs):
	a_depth_of_friends = list()
	for f in fs:
		a_depth_of_friends += get_friends('https://api.venmo.com/v1/users/' + f['id'] + '/friends?limit=50')
	return remove_duplicates(a_depth_of_friends)

# Function to subtract one list of dicts from another
def subtract_list_of_dicts(minuend, subtrahend):
	mi = Counter([tuple(m.items()) for m in minuend])
	su = Counter([tuple(s.items()) for s in subtrahend])
	diff = list((mi - su).elements())
	return [dict(d) for d in diff]

# Get friends to desired depth, starting from myself
friends = list()
friends_looked_up = list()
friends_to_look_up = [{'id': id_mine}]
direct_friends = None
if verbose:
	print 'Start to get friends'
for _ in range(lookup_depth):
	friends_looked_up += friends_to_look_up[:]
	friends_to_look_up = get_a_depth_of_friends(friends_to_look_up)
	friends += friends_to_look_up[:]
	if direct_friends is None:
		direct_friends = friends_to_look_up[:]
	friends_to_look_up = subtract_list_of_dicts(friends_to_look_up, friends_looked_up)

friends = remove_duplicates(friends)
if verbose:
	print 'and that\'s it'
	print 'Removed duplicates from the result'
if no_friends:
	friends = subtract_list_of_dicts(friends, direct_friends)
	if verbose:
		print 'Removed direct friends from the result'
		print

# Ask to continue or not
print
print 'Got total ' + str(len(friends)) + ' Venmo friends'
if limit_request is not None:
	print 'Limit is set to ' + str(limit_request) + ' friends'
should_continue = raw_input('Do you wish to continue? (y/n) ')
if not should_continue.lower() in ('y', 'yes', 'yeah', 'sure', 'absolutely'):
	print 'Okay, bye'
	sys.exit()

print
print 'Charging everybody!'

# Charge everyone!
error_num = 0
error_list = list()
done_count = 0
for f in friends:
	params = {'access_token': access_token, 'user_id': f['id'], 'note': note, 'amount': charge_amount}
	if audience is not None:
		params['audience'] = audience
	result = requests.post('https://api.venmo.com/v1/payments', data=params).json()
	try:
		error_list.append(result['error'])
		error_num += 1
	except KeyError:
		pass
	print f['display_name'] + ',',
	done_count += 1
	if limit_request is not None:
		limit_request -= 1
		if limit_request == 0:
			print 'and that\'s it'
			print 'Hit the limit set'
			break

# Check results
if limit_request is None:
	print 'and that\'s it'
print
if error_num > 0:
	print str(error_num) + ' error(s) occured during the process:'
	print
	for e in error_list:
		print e['message'] + ' (' + str(e['code']) + ')'
	print
	print 'Process finished with some errors (' + str(done_count - len(error_list)) + '/' + str(done_count) + ')'
else:
	print 'Charging successfully finished! (' + str(done_count) + ')'

print 'Note: ' + note
print 'Charge amount: ' + str(-charge_amount)
if audience is not None:
	print 'Audience: ' + audience