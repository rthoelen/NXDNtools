import socket
import sys
import struct
import collections
import threading
import time
import csv

from kw_rpt_list import rpt_list
from tg_dict import tg_dict

OUTPUT_HTMLFILE = "/var/www/html/kenwood.html"

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
		outfile.write("</head><body><center><h2>NXCM Kenwood Log</h2></center>")
		outfile.write("<br/><br/><br/><p>")
		outfile.write("<p><center>Don't see your name with your ID?  Sign up at <a href='http://nxmanager.weebly.com'>http://nxmanager.net/</a></center></p>")
		outfile.write("<br/><br/><br/><p>")
		outfile.write("<table border='1' width='100%' style='border-collapse:collapse'><tr><td width='260'><b>Last Heard</b></td><td width='400'><b>User / UID</b></td> \
			<td width='200'><b>Talkgroup / GID</b></td><td width='200'><b>Repeater</b></td><td><b>RX RAN</b></td><td width='90'><b>Status</b></td></b></tr>")
		for i in range(0,len(packetlist)):
			outfile.write(packetlist[i])
			outfile.write("\n")
		outfile.write("</table></p></body></html>")
		outfile.close()


t = threading.Thread(target=writeout)
t.start()

uid_dict = {}
with open('nxdn.csv') as csvfile:
	uidreader = csv.reader(csvfile, delimiter=',', quotechar='|')
	for row in uidreader:
                if len(row) < 1:
                    continue
		if row[0].isdigit():
			tempstr = row[1] + "  -  " + row[2]
			if len(row[3]) > 0:
				tempstr += "  -  " + row[3]
			tempstr +=  "<br/>(<b>" + row[0] + "</b>)"
			uid_dict[row[0]] = tempstr
		else:
			uid_dict[row[0]] = row[0]


log_dict = {}

while True:
    data, addr = sock.recvfrom(60)
    key = 0
    key = int(ord(data[8]))
    key = int(key + (ord(data[9]) << 8));
    key = int(key + (ord(data[10]) << 16));
    key = int(key + (ord(data[11]) << 24));
    if (len(data) == 47):

	if ord(data[20]) != 0x0a:
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
		log_dict[key] = [uidstr, gidstr, RAN, rpt, 0]
		continue
        
	if ord(data[28]) == 8:
		
		if key in log_dict:
			l = log_dict[key]
			packetlist.appendleft("<tr bgcolor='#87CEFA'><td><center> "+ time.strftime("%c, %z") + "</center></td><td><center> " + l[0] + "</center></td><td><center> " + l[1] + "</center></td><td><center> " + l[3] + "</center></td><td><center>" + str(l[2]) + "</center></td><td><center>PTT Off</center></td></tr>")
			del log_dict[key]
		continue


	if (ord(data[23]) == 0x01) and (ord(data[28]) == 0x3f):

		if key in log_dict:
			ot_str = data[31] + data[34] + data[33] + data[36]
			ot_str += data[41] + data[44] + data[43] + data[46]
			l = log_dict[key]
			l.append(ot_str)
			log_dict[key] = l

		continue

	if (ord(data[23]) == 0x80) and (ord(data[28]) == 0x3f):

		if key in log_dict:
			l = log_dict[key]
			ot_str = data[31] + data[34] + data[33] + data[36]
			ot_str += data[41] + data[44]
			if len(l) == 6:
				l[5] = l[5] + ot_str
			if len(l) == 5:
				l.append(ot_str)
			log_dict[key] = l

		continue




    if len(data) == 59:

	if key in log_dict:

		l = log_dict[key]
		if l[4] == 1:
			continue
		if len(l) == 5: 
			packetlist.appendleft("<tr><td><center> "+ time.strftime("%c, %z") + "</center></td><td><center> " + l[0] + "</center></td><td><center> " + l[1] + "</center></td><td><center> " + l[3] + "</center></td><td><center>" + str(l[2]) + "</center></td><td><center>PTT On</center></td></tr>")
		if len(l) == 6:
			packetlist.appendleft("<tr><td><center> "+ time.strftime("%c, %z") + "</center></td><td><center> " + l[0] + "<br/>OTAA: <b>" + l[5] + "</b></center></td><td><center> " + l[1] + "</center></td><td><center> " + l[3] + "</center></td><td><center>" + str(l[2]) + "</center></td><td><center>PTT On</center></td></tr>")
		l[4] = 1 
		log_dict[key] = l
	continue


