import socket
import sys
import struct
import collections
import threading
import time
import csv

from kw_rpt_list import rpt_list
from tg_dict import tg_dict

OUTPUT_HTMLFILE = "/usr/local/www/nginx/kenwood.html"

UDP_IP = "127.0.0.1"
UDP_PORT = 50000
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

packetlist = collections.deque(maxlen=600)

def writeout():

	while True:
		time.sleep(15)
		outfile = open(OUTPUT_HTMLFILE, 'w')
		outfile.write("<html><head><title>Kenwood NXDN Log</title>")
		outfile.write("<meta http-equiv='refresh' content='10'>")
		outfile.write("</head><body><center><h2>N1XDN Connecticut NXCM log</h2></center>")
		outfile.write("<br/><br/><br/><p>")
		outfile.write("<table border='1' style='border-collapse:collapse'><tr><td width='260'><b>Last Heard</b></td><td width='250'><b>User / UID</b></td> \
			<td width='250'><b>Talkgroup / GID</b></td><td width='200'><b>Repeater</b></td><td><b>RX RAN</b></td><td width='90'><b>Status</b></td></b></tr>")
		for i in range(0,len(packetlist)):
			outfile.write(packetlist[i])
			outfile.write("\n")
		outfile.write("</table></p></body></html>")
		outfile.close()


t = threading.Thread(target=writeout)
t.start()

uid_dict = {}
with open('uid.csv') as csvfile:
	uidreader = csv.reader(csvfile, delimiter=',', quotechar='|')
	for row in uidreader:
		if row[0].isdigit():
			tempstr = row[1] + "  -  " + row[2]
			if len(row[3]) > 0:
				tempstr += "  -  " + row[3]
			tempstr +=  "<br/>(<b>" + row[0] + "</b>)"
			uid_dict[row[0]] = tempstr
		else:
			uid_dict[row[0]] = row[0]



while True:
    data, addr = sock.recvfrom(59) # buffer size is 1024 bytes
    h = ":".join("{0:x}".format(ord(c)) for c in data)
    if (len(data) == 47):
#        d = struct.unpack(">HHHHHHHHHHHHBBBB",data)
#        print "unpacked:", d

	if ord(data[20]) != 0x0a or ord(data[23]) != 0x10 or ord(data[29]) == 0x36:
		continue

	UID = (ord(data[29]) << 8) + ord(data[32])
	GID = (ord(data[31]) << 8) + ord(data[34])
	RAN = ord(data[24])
	if (UID == 0):
		continue

	rpt = ""

	for item in rpt_list:
		if (ord(data[8])==item[3]) and (ord(data[9])==item[2]) and (ord(data[10])==item[1]) and (ord(data[11])==item[0]):
			rpt = item[4]

	gidstr = tg_dict.get(GID)
	if not gidstr:
		gidstr = str(GID)

	uidstr = uid_dict.get(str(UID))
	if not uidstr:
		uidstr = str(UID)
        
	if ord(data[28]) == 1:
		packetlist.appendleft("<tr><td><center> "+ time.strftime("%c, %z") + "</center></td><td><center> " + uidstr + "</center></td><td><center> " + gidstr + "</center></td><td><center> " + rpt + "</center></td><td><center>" + str(RAN) + "</center></td><td><center>PTT On</center></td></tr>")
	else:
		packetlist.appendleft("<tr bgcolor='#87CEFA'><td><center> "+ time.strftime("%c, %z") + "</center></td><td><center> " + uidstr + "</center></td><td><center> " + gidstr + "</center></td><td><center> " + rpt + "</center></td><td><center>" + str(RAN) + "</center></td><td><center>PTT Off</center></td></tr>")
