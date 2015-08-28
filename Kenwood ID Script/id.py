#Copyright (C) 2015 Robert Thoelen
#Version 1.0.2

#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at

#http://www.apache.org/licenses/LICENSE-2.0

#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

import socket
import sys
import struct
import string
import time

#################
# Things to edit

# Repeater IP
R_IP = "192.168.1.54"

# Pi IP

P_IP = "192.168.1.55"

RAN = 1
GID = 0
UID = 929

# To keep things simple, message must be 14 characters long
# If shorter than 14 chars, add spaces to get to 14

MESSAGE = "ENFLD NEXEDGE "
################

# Some definitions

UDP_PORT = 64001
UDP_PORT2 = 64000
SEQ = 0xf1

# First, unpack UID and GID

UID1 = UID >> 8
UID2 = UID & 0xff

# GID needs to be reverse

GID1 = GID >> 8
GID2 = GID & 0xff



# Extract IP address
[IP1,IP2,IP3,IP4] = struct.unpack("!BBBB",socket.inet_aton(R_IP))
[IP5,IP6,IP7,IP8] = struct.unpack("!BBBB",socket.inet_aton(P_IP))



sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

# This string keys up the repeater
string = struct.pack('>HHBBBBHHHHHHHBBBBH',0x8acc, 0x0006, IP8,IP7,IP6,IP5,0x4b57,0x4e45,0, 0,0,0,0,2,0,RAN,0,0)
sock.sendto(string, (R_IP, UDP_PORT))
time.sleep(0.05)
sock.sendto(string, (R_IP, UDP_PORT))
time.sleep(0.05)
sock.sendto(string, (R_IP, UDP_PORT))
time.sleep(0.05)

# This next packet sends UID/GID and other info
string = struct.pack('>HBBHHBBBBHHHHHHBBHBBBBBBBBHBBBBBBBB', 0x8066, 0x31, SEQ, 0x7499, 0xcf6e, IP4, IP3, IP2, IP1,
	0x0000, 0x0000, 0x0303, 0x0404, 0x0a05, 0x0a10,
	RAN, 0x00,0x0000, 0x01, UID1, 0x20,GID1, UID2, 0x00, GID2, 0x00, 0x0000,  0x01, UID1,
	0x20, GID1, UID2, 0x00, GID2, 0x00)   # GID is 0000
sock.sendto(string, (R_IP, UDP_PORT2))

time.sleep(0.2)

# Update sequence identifier

SEQ += 1


# This packet is first 8 chars of OTAA


string = struct.pack('>HBBHHBBBBHHHHHHHHHBBBBBBBBHBBBBBBB', 0x8066, 0x31, SEQ, 0x7499, 0xcf6e, IP4, IP3, IP2, IP1,
	0x0000, 0x0000, 0x0303, 0x0404, 0x0a05, 0x0a01, 0xd600, 0x0068, 0x3f04, 0x82, ord(MESSAGE[0]), 0x14,
	ord(MESSAGE[2]), ord(MESSAGE[1]), 0x00, ord(MESSAGE[3]), 0x68, 0x3f04, 0x82, ord(MESSAGE[4]), 0x24,
	ord(MESSAGE[6]), ord(MESSAGE[5]), 0x00, ord(MESSAGE[7]))
	
sock.sendto(string, (R_IP, UDP_PORT2))
time.sleep(0.1)

# Update sequence identifier

SEQ += 1

# This packet is last 8 chars of OTAA

string = struct.pack('>HBBHHBBBBHHHHHHHHHBBBBBBBBHBBBBBBB', 0x8066, 0x31, SEQ, 0x7499, 0xcf6e, IP4, IP3, IP2, IP1,
	0x0000, 0x0000, 0x0303, 0x0404, 0x0a05, 0x0a80, 0x9640, 0x0e68, 0x3f04, 0x82, ord(MESSAGE[8]), 0x34,
	ord(MESSAGE[10]), ord(MESSAGE[9]), 0x00, ord(MESSAGE[11]), 0x68, 0x3f04, 0x82, ord(MESSAGE[12]), 0x44,
	0x02, ord(MESSAGE[13]), 0x00, 0xa7)


sock.sendto(string, (R_IP, UDP_PORT2))
time.sleep(0.2)


# This string signals end of transmission
string = struct.pack('>HHBBBBHHHHHH',0x8bcc, 0x0004, IP8,IP7,IP6,IP5,0x4b57,0x4e45, UID, GID,0x0100,0)
sock.sendto(string, (R_IP, UDP_PORT))
time.sleep(0.2)
sock.sendto(string,(R_IP, UDP_PORT))
time.sleep(0.2)
sock.sendto(string, (R_IP, UDP_PORT))
sock.close()

