import socket
import sys
import struct
import datetime
import collections
import threading
import time

OUTPUT_HTMLFILE = "/usr/local/www/nginx/kenwood.html"

UDP_IP = "0.0.0.0"
UDP_PORT = 64000
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

packetlist = collections.deque(maxlen=400)

def writeout():

	while True:
		time.sleep(15)
		outfile = open(OUTPUT_HTMLFILE, 'w')
		outfile.write("<html><head><title>Kenwood NXDN WW Net Log</title>")
		outfile.write("<meta http-equiv='refresh' content='10'>")
		outfile.write("</head><body><center><h2>Kenwood WW Net Log</h2></center>")
		outfile.write("<br/><br/><br/><p>")
		for i in range(0,len(packetlist)):
			outfile.write(packetlist[i])
			outfile.write("\n")
			outfile.write("<br/>")
		outfile.write("</p></body></html>")
		outfile.close()


t = threading.Thread(target=writeout)
t.start()

while True:
    data, addr = sock.recvfrom(59) # buffer size is 1024 bytes
    h = ":".join("{0:x}".format(ord(c)) for c in data)
    if (len(data) == 47):
#        d = struct.unpack(">HHHHHHHHHHHHBBBB",data)
#        print "unpacked:", d
	UID = (ord(data[29]) << 8) + ord(data[32])
	GID = (ord(data[31]) << 8) + ord(data[34])
	if UID == 0:
		continue
        
	if ord(data[28]) == 1:
		packetlist.appendleft("Timestamp: "+ str(datetime.datetime.utcnow()) + " - UID: " + str(UID) + " - GID: " + str(GID) + " - PTT On")
	else:
        	packetlist.appendleft("Timestamp: " + str(datetime.datetime.utcnow()) + " - UID: " + str(UID)  + " - GID: " + str(GID) + " - PTT Off") 
