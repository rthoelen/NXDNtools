import socket
import sys
import struct
import collections
import threading
import time

OUTPUT_HTMLFILE = "/usr/local/www/nginx/icom.html"

UDP_IP = "0.0.0.0"
UDP_PORT = 41300
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

packetlist = collections.deque(maxlen=400)

def writeout():

	while True:
		time.sleep(15)
		outfile = open(OUTPUT_HTMLFILE, 'w')
		outfile.write("<html><head><title>Icom NXDN WW Net Log</title>")
		outfile.write("<meta http-equiv='refresh' content='10'>")
		outfile.write("</head><body><center><h2>N1XDN Icom WW Net Log</h2></center>")
		outfile.write("<br/><br/><br/><p>")
		outfile.write("<table border='1'><tr><td width='300'>Last Heard</td><td width='150'>UID</td><td width='150'>GID</td><td width='200'>Status</td></tr>")
		for i in range(0,len(packetlist)):
			outfile.write(packetlist[i])
			outfile.write("\n")
		outfile.write("</table></p></body></html>")
		outfile.close()


t = threading.Thread(target=writeout)
t.start()

while True:
    data, addr = sock.recvfrom(105) # buffer size is 1024 bytes
    h = ":".join("{0:x}".format(ord(c)) for c in data)
    if (ord(data[38]) == 0x1c):
#        d = struct.unpack(">HHHHHHHHHHHHBBBB",data)
#        print "unpacked:", d
	UID = (ord(data[48]) << 8) + ord(data[49])
	GID = (ord(data[50]) << 8) + ord(data[51])
	if (UID == 0) or (GID==0):
		continue
        
	if ord(data[45]) == 1:
		packetlist.appendleft("<tr><td> "+ time.strftime("%c, %z") + "</td><td> " + str(UID) + "</td><td> " + str(GID) + "</td><td> PTT On</td></tr>")
	else:
		packetlist.appendleft("<tr><td> "+ time.strftime("%c, %z") + "</td><td> " + str(UID) + "</td><td> " + str(GID) + "</td><td> PTT Off</td></tr>")
