from socket import *
import os
import sys
import struct
import time
import select

# ICMP types
ICMP_ECHO_REPLY = 0
ICMP_ECHO_REQUEST = 8
ICMP_TIME_EXCEEDED = 11

# Set same number as normal traceroute
MAX_HOPS = 64


def checksum(string):
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = string[count + 1] * 256 + string[count]
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2

    if countTo < len(string):
        csum = csum + string[len(string) - 1]
        csum = csum & 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


# Make packet in the same way we did for ping
def make_packet():
    my_checksum = 0
    my_id = os.getpid() & 0xFFFF  # Return the current process id

    # Make a dummy header with a 0 checksum
    header = struct.pack("BBHHH", ICMP_ECHO_REQUEST, 0, my_checksum, my_id, 1)
    data = struct.pack("d", time.time())
    # Calculate the checksum on the data and the dummy header.
    my_checksum = checksum(header + data)

    # Get the right checksum, and put it in the header
    if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network byte order
        my_checksum = htons(my_checksum) & 0xffff
    else:
        my_checksum = htons(my_checksum)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, my_id, 1)
    packet = header + data
    return packet


# Get the name of the router from a given IP (Optional Excercise)
def get_addr_name(addr):
    try:
        return gethostbyaddr(addr)[0]
    except herror:  # Unknown
        return addr


# Perform traceroute to the next router
def single_traceroute(dest, ttl, timeout, time_left):
    icmp = getprotobyname("icmp")
    raw_socket = socket(AF_INET, SOCK_RAW, icmp)
    raw_socket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
    raw_socket.settimeout(timeout)

    try:
        packet = make_packet()
        raw_socket.sendto(packet, (dest, 0))
        time_sent = time.time()

        started_select = time.time()
        what_ready = select.select([raw_socket], [], [], time_left)
        time_in_select = time.time() - started_select
        if what_ready[0] == []:  # Timeout
            print("%d   Timeout: Socket not ready" % ttl)
            return time_left - (time.time() - started_select)

        time_left = time_left - time_in_select
        if time_left <= 0:  # Timeout
            print("%d   Timeout: No time left" % ttl)
            return time_left

        time_received = time.time()
        rec_packet, addr = raw_socket.recvfrom(1024)
        icmp_header = rec_packet[20:28]
        icmp_type, code, checksum, packetID, sequence = struct.unpack(
            "bbHHh", icmp_header)

        if icmp_type == ICMP_TIME_EXCEEDED:  # TTL is 0
            addr_name = get_addr_name(addr[0])
            print("%d   %s (%s)  %.2f ms" % (ttl, addr_name, addr[0],
                                             (time_received - time_sent)
                                             * 1000))
            return time_left
        elif icmp_type == ICMP_ECHO_REPLY:  # Final destination replied
            # Get time_sent
            byte = struct.calcsize("d")
            time_sent = struct.unpack("d", rec_packet[28:28 + byte])[0]
            addr_name = get_addr_name(addr[0])
            print("%d   %s (%s)  %.2f ms" % (ttl, addr_name, addr[0],
                                             (time_received - time_sent)
                                             * 1000))
            return -1
        else:  # Handle other icmp_type
            print("%d   icmp_type: %s   %s (%s)  %.2f ms" % (
                ttl, icmp_type, addr_name, addr[0],
                 (time_received - time_sent) * 1000))
            return time_left
    finally:  # Close socket every time
        raw_socket.close()


# Traceroute until we reach the destination host or MAX_HOPS
# Need to set timeout to be longer for some hosts
def traceroute(host, timeout=1):
    time_left = timeout
    dest = gethostbyname(host)
    print("Traceroute to " + host + " (%s) using Python, %d hops max:"
          % (dest, MAX_HOPS))

    # Increasing TTL
    for ttl in range(1, MAX_HOPS):
        time_left = single_traceroute(dest, ttl, timeout, time_left)
        if time_left <= 0:
            break

    if ttl == MAX_HOPS:
        print("Timeout: Exceeded %d hops" % MAX_HOPS)

    return


if __name__ == '__main__':
    host = sys.argv[1]
    traceroute(host, timeout=15)

    # traceroute("google.com", timeout=10)
    # traceroute("www.suzunoya.com", timeout=15)
    # traceroute("facebook.com", timeout=10)
    # traceroute("engineering.columbia.edu", timeout=10)
