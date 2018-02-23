#!/usr/bin/env python

import socket
import sys
import time
import argparse

# Fuzz a HTTP server:
#   ./ez_poison.py --target 192.168.56.101:80 --prepend 'GET /' --append '\r\n\r\n' --bad '\x00\x0a\x0d'
#
# Fuzz a TFTP server (Transporting Mode):
#   ./ez_poison.py --target 192.168.56.101:69 --udp --prepend "\x00\x02filename\x00" --append "\x00" --bad "\x00"
#
# Combine with Immunity Debugger's !packets command for a quick and easy crash monitor.

parser = argparse.ArgumentParser(description="fuzz mindlessly with one line, see source for examples.")
parser.add_argument('--target', help='target, as in <ipaddress>:<port>.')
parser.add_argument('--udp', action='store_true', help='UDP mode.')
parser.add_argument('--banner', action='store_true', help='grab banner/recv data on connection.')
parser.add_argument('--prepend', action='store', type=str, help='data to prepend to the packet.')
parser.add_argument('--append', action='store', type=str, help='data to append to the packet.')
parser.add_argument('--bad', action='store', type=str, help='exclude bad characters (eg "\\x00\\x0a").')
parser.add_argument('--multiple', action='store', type=int, help='multiple to increase buffer size by.')
parser.add_argument('--max', action='store', type=int, help='maximum buffer size.')
parser.add_argument('--wait', action='store', type=int, help='wait time between connections (secs).')
args = parser.parse_args()

print """
                                                 oo                            
                                                                               
.d8888b. d888888b              88d888b. .d8888b. dP .d8888b. .d8888b. 88d888b. 
88ooood8    .d8P'              88'  `88 88'  `88 88 Y8ooooo. 88'  `88 88'  `88 
88.  ...  .Y8P                 88.  .88 88.  .88 88       88 88.  .88 88    88 
`88888P' d888888P              88Y888P' `88888P' dP `88888P' `88888P' dP    dP 
                  oooooooooooo 88                                              
                               dP                                              

                               clueless fuzzer
                                   @3xocyte
"""

#get target info
delim = args.target.index(':')
rhost = args.target[:delim]
rport = int(args.target[delim+1:])

# todo: sqlmap-style templates
# generate file testcases
    
# optional stuff:
if args.prepend: raw_prep = eval('"' + args.prepend.replace('"', '\\"') + '"')
if args.append: raw_app = eval('"' + args.append.replace('"', '\\"') + '"')
if args.bad: bad = eval('"' + args.bad.replace('"', '\\"') + '"')
    
if args.max:
    maximum = args.max
else:
    maximum = 10000

if args.multiple:
    multiple = args.multiple
else:
    multiple = 250

if args.wait:
    wait = args.wait
else:
    wait = 1

def send_payload(payload):
    if args.udp:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(payload, (rhost, rport))
        s.recvfrom(1024)
        s.close()
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((rhost, rport))
        if args.banner: s.recv(1024)
        s.send(raw_prep + current_byte * i + raw_app)
        s.recv(1024)
        s.close()

# generate all the characters
chars = []
i = 0
while i < 256:
    chars.append(i)
    i += 1

# for each allowed character, send increasingly large buffers
for c in chars:
    current_byte = bytes(bytearray([c])) # get the byte itself
    current_char =  '\\x{:02x}'.format(c) # to get exploit dev-friendly feedback
    if current_byte not in bad: # skip banned characters
        i = 0
        while i <= maximum:
            if i == 0: i = 1
            print "[*] sending \"" + current_char + "\" x " + str(i) + "..."
            send_payload(raw_prep + current_byte * i + raw_app)
            if i == 1: i = 0
            i = i + multiple
            time.sleep(wait)
        print "\n"
