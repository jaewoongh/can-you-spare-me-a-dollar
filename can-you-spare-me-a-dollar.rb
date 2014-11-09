#!/usr/bin/env ruby

require 'optparse'
require 'net/http'
require 'json'

# Parse options
options = { :note => "Can you spare me a dollar?", :charge => -1, :depth => 1, :nofriends => false, :verbose => false }
o = OptionParser.new do |opts|
	opts.banner = "Usage: ./can-you-spare-me-a-dollar.rb [options]"

	opts.on("-t", "--token t", "(REQ) Venmo developer access token") do |t|
		options[:token] = t
	end

	opts.on("-n", "--note n", "Note for the transaction") do |n|
		options[:note] = n
	end

	opts.on("-c", "--charge c", "Amount to charge. Minus value for payment") do |c|
		begin c = Float c
		rescue ArgumentError
			puts 'Invalid charge amount; should be a number'
			puts o
			exit 1
		end
		options[:charge] = -c
	end

	opts.on("-a", "--audience a", "Sharing setting for the transaction (public|friends|private)") do |a|
		unless ['public', 'friends', 'private'].include?(a.downcase)
			puts 'Invalid audience option'
			puts o
			exit 1
		end
		options[:audience] = a
	end

	opts.on("-d", "--depth d", "If specified, get friends' friends' friends..") do |d|
		begin d = Integer d
		rescue ArgumentError
			puts 'Invalid depth value; should be a number'
			puts o
			exit 1
		end
		options[:depth] = d
	end

	opts.on("-l", "--limit l", "Limit charging request not to exceed this number") do |l|
		begin l = Integer l
		rescue ArgumentError
			puts 'Invalid limit value; should be a number'
			puts o
			exit 1
		end
		options[:limit] = l
	end

	opts.on("-F", "--no-friends", "Don't charge your direct friends") do |f|
		options[:nofriends] = true
	end

	opts.on("-v", "--verbose", "Be verbose") do |v|
		options[:verbose] = true
	end
end

begin o.parse! ARGV
rescue OptionParser::InvalidOption => e
	puts e
	puts o
	exit 1
end

if options[:token].nil?
	puts 'You need to give an access token'
	puts o
	exit 1
end

# Handle API error response
def handle_error(e)
	puts "#{e["message"]} (#{e["code"]})"
	exit 1
end

# Get my id
me = JSON.parse(Net::HTTP.get(URI("https://api.venmo.com/v1/me?access_token=#{options[:token]}")))
unless me["error"].nil?
	handle_error me["error"]
end
id_mine = me["data"]["user"]["id"]

# Function for getting a page of friends
def get_a_page_of_friends(req, opts)
	friends_got = JSON.parse(Net::HTTP.get(URI("#{req}&access_token=#{opts[:token]}")))
	unless friends_got["error"].nil?
		handle_error friends_got["error"]
	end
	if opts[:verbose]
		friends_got["data"].each do |f|
			print "#{f["display_name"]}, "
		end
	end
	friends_got
end

# Function for getting friends looking through many pages if neccessary
def get_friends(req, opts)
	pages_of_friends = Array.new
	a_page_of_friends = get_a_page_of_friends(req, opts)
	pages_of_friends = Marshal.load(Marshal.dump(a_page_of_friends["data"]))	# Deep copy
	while true do
		next_page = a_page_of_friends["pagination"]["next"]
		if next_page.nil?
			break
		else
			a_page_of_friends = get_a_page_of_friends(next_page, opts)
			pages_of_friends += Marshal.load(Marshal.dump(a_page_of_friends["data"]))
		end
	end
	pages_of_friends
end

# Function for getting friends over and over to desired depth
def get_a_depth_of_friends(fs, opts)
	a_depth_of_friends = Array.new
	fs.each do |f|
		a_depth_of_friends += get_friends("https://api.venmo.com/v1/users/#{f["id"]}/friends?limit=50", opts)
	end
	a_depth_of_friends.uniq
end

# Get friends to desired depth, starting from myself
friends = Array.new
friends_looked_up = Array.new
friends_to_look_up = [{"id" => id_mine}]
direct_friends = nil
if options[:verbose]
	puts 'Start to get friends'
end
options[:depth].times do
	friends_looked_up += Marshal.load(Marshal.dump(friends_to_look_up))
	friends_to_look_up = get_a_depth_of_friends(friends_to_look_up, options)
	friends += Marshal.load(Marshal.dump(friends_to_look_up))
	direct_friends = Marshal.load(Marshal.dump(friends_to_look_up)) if direct_friends.nil?
	friends_to_look_up -= friends_looked_up
end

friends = friends.uniq	# Remove duplicated ones
if options[:verbose]
	puts 'and that\'s it'
	puts 'Removed duplicates from the result'
end
if options[:nofriends]
	friends -= direct_friends
	if options[:verbose]
		puts 'Removed direct friends from the result'
		puts
	end
end

# Ask to continue or not
puts
puts "Got total #{friends.size} Venmo friends"
unless options[:limit].nil?
	puts "Limit is set to #{options[:limit]} friends"
end
print 'Do you wish to continue? (y/n) '
should_continue = STDIN.gets.chomp()
unless ['y', 'yes', 'yeah', 'sure', 'absolutely'].include? should_continue.downcase
	puts 'Okay, bye'
	exit
end

if options[:verbose]
	puts
	puts 'Charging everybody!'
end

# Charge everyone!
error_num = 0
error_list = Array.new
done_count = 0
friends.each do |f|
	params = {'access_token' => options[:token], 'user_id' => f["id"], 'note' => options[:note], 'amount' => options[:charge]}
	params['audience'] = options[:audience] unless options[:audience].nil?
	result = JSON.parse(Net::HTTP.post_form(URI("https://api.venmo.com/v1/payments"), params).body)
	unless result["error"].nil?
		error_list.push(result["error"])
		error_num += 1
	end
	print "#{f["display_name"]}, " if options[:verbose]
	done_count += 1
	unless options[:limit].nil?
		options[:limit] -= 1
		if options[:limit] == 0
			if options[:verbose]
				puts 'and that\'s it'
				puts 'Hit the limit set'
			end
			break
		end
	end
end

# Check results
puts 'and that\'s it' if (options[:limit].nil? and options[:verbose])
puts
if error_num > 0
	puts "#{error_num} error(s) occured during the process:"
	puts
	error_list.each do |e|
		puts "#{e["message"]} (#{e["code"]})"
	end
	puts "Process finished with some errors (#{done_count - error_num}/#{done_count})"
else
	puts "Charging successfully finished! (#{done_count})"
end

puts "Note: #{options[:note]}"
puts "Charge amount: #{-options[:charge]}"
puts "Audience: #{options[:audience]}" unless options[:audience].nil?