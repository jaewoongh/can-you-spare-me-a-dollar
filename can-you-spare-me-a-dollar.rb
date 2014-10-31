#!/usr/bin/env ruby

require 'optparse'
require 'net/http'
require 'json'

# Parse options
options = { :note => "Can you spare me a dollar?", :charge => -1 }
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

# Get friends' id
def get_friends(req, tok)
	friends_got = JSON.parse(Net::HTTP.get(URI("#{req}&access_token=#{tok}")))
	unless friends_got["error"].nil?
		handle_error friends_got["error"]
	end
	friends = friends_got["data"]
	fids = Array.new
	friends.each do |f|
		fids.push(f["id"])
	end
	{ :next => friends_got["pagination"]["next"], :ids => fids }
end

a_page_of_friends = get_friends("https://api.venmo.com/v1/users/#{id_mine}/friends?limit=50", options[:token])
id_friends = a_page_of_friends[:ids]
while true do
	next_page = a_page_of_friends[:next]
	break if next_page.nil?
	a_page_of_friends = get_friends(next_page, options[:token])
	id_friends += a_page_of_friends[:ids]
end

# Charge everyone!
error_num = 0
error_list = Array.new
id_friends.each do |id|
	params = { 'access_token' => options[:token], 'user_id' => id, 'note' => options[:note], 'amount' => options[:charge] }
	params['audience'] = options[:audience] unless options[:audience].nil?
	result = JSON.parse(Net::HTTP.post_form(URI("https://api.venmo.com/v1/payments"), params).body)
	unless result["error"].nil?
		error_list.push(result["error"])
		error_num += 1
	end
end

# Check results
if error_num > 0
	puts "#{error_num} error(s) occured during the process:"
	puts
	error_list.each do |e|
		puts "#{e["message"]} (#{e["code"]})"
	end
	puts "Process finished with some errors (#{id_friends.size - error_num}/#{id_friends.size})"
else
	puts "Charging successfully finished! (#{id_friends.size})"
end

puts "Note: #{options[:note]}"
puts "Charge amount: #{options[:charge]}"
puts "Audience: #{options[:audience]}" unless options[:audience].nil?