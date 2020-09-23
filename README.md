# Traceroute
Written in Python using raw sockets, ICMP request, and reply messages.
Screenshots to verify results are in the directory.

## IcmpPing.py
Ping is a computer network app to test whether a particular host is reachable across an IP network. It sends ICMP echo request packets to the target and listens for ICMP echo reply packets. 
In order to keep it simple, this program does not follow the official spec in RFC 1739. 
This ping app is the client side and utlizes the server side built in the OS. This means that it will send a ping requests containing data and timestamp seperated by 1 second. After sending each packet, it will wait up to 1 second to receive a reply and if it surpasses 1 second, it assumes that the ping or pong packet was lost in the network. 

### Instructions
To run IcmpPing.py: `sudo python3 IcmpPing.py [URL]`

Three examples, commented out, for the host are included in the main method.

## Traceroute.py
Traceroute is a diagnostic tool that allows a user to trace the route from a host to any other host. It works by sending a ICMP echo messages to the same destination with increasing TTL field and the routers along the path return ICMP Time Exceeded if TTL reaches 0. The final destination will send an ICMP reply if it receives the echo request. The IP addresses of the routers can be extracted from the received packets and the RTT can be measured by a timer at the sending host.
This app will print out a list of IP addresses of all routers in the path from source to destination and the RTT.

### Instructions
To run Traceroute.py: `sudo python3 Traceroute.py [URL]`

Four different target hosts were tested including google.com, suzunoya.com,
facebook.com, and engineering.columbia.edu.
Screenshots to verify results are in the directory.

## Environment
$ python3 --version
Python 3.7.3
$ uname
Darwin

## About ICMP
ICMP header starts after bit 160 of IP header

### Echo request
- Type is 8
- Code is 0
- Data received with echo request must be included in echo reply

### Echo Reply
- Type is 0
- Code is 0 
- Data received with echo request must be included in echo reply
