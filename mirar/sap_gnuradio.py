#!/usr/bin/env python

import sap
import socket
import time

import random

class HashRegister:

	def __init__(self):
		self.HashTable = range(0, 256)
		random.shuffle(self.HashTable)
		self.InUse = []

	def hash8(self, message, h):
		hash = h % 256
		for i in message:
			hash = self.HashTable[hash^ord(i)]
		return hash

	def hash16(self, message):
		hash1 = self.hash8(message, random.randint(0,255))
		hash2 = self.hash8(message, random.randint(0,255))
		hash = (hash2<<8) + hash1
		return hash

	def getHashId(self, message):
		i = 0
		while i < 50:
			hash = self.hash16(message)	
			if hash not in self.InUse :
				self.InUse.append(hash)
				return hash
			i = i + 1
		return -1

	def delHashId(self, hashId):
		if hashId in self.InUse :
			self.InUse.remove(hashId)

SDP = """v=0
o=mhandley 2890844526 2890842807 IN IP4 126.16.64.4
s=SDP Seminar
i=A Seminar on the session description protocol
u=http://www.cs.ucl.ac.uk/staff/M.Handley/sdp.03.ps
e=mjh@isi.edu (Mark Handley)
c=IN IP4 224.2.17.12/127

t=2873397496 2873404696
a=recvonly
m=audio 49170 RTP/AVP 0
m=video 51372 RTP/AVP 31
m=application 32416 udp wb
a=orient:portrait"""

SDP2 = """v=0
o=mjou 2890844526 2890842807 IN IP4 122.1.64.4
s=SDP2 Seminar
i=A Seminar on the session description protocol
u=http://www.cs.ucl.ac.uk/staff/M.Handley/sdp.03.ps
e=mjh@isi.edu (Mark Handley)
c=IN IP4 224.2.17.11/127

t=2873397496 2873404696
a=recvonly
m=audio 49170 RTP/AVP 0
m=video 51372 RTP/AVP 31
m=application 32416 udp wb
a=orient:portrait"""

SDP3 = """v=0
o=mjouny 2890844526 2890842807 IN IP4 122.1.64.4
s=SDP2 Seminar
i=A Seminar on the session description protocol
u=http://www.cs.ucl.ac.uk/staff/M.Handley/sdp.03.ps
e=mjh@isi.edu (Mark Handley)
c=IN IP4 224.2.17.11/127

t=2873397496 2873404696
a=recvonly
m=audio 49170 RTP/AVP 0
m=video 51372 RTP/AVP 31
m=application 32416 udp wb
a=orient:portrait"""


def check_msg(newMsg):
	global msg_list
	global HashTable


	if len(msg_list) == 0:
		hashid = HashTable.getHashId(newMsg._payload)
		newMsg.setMsgHash(hashid)
		msg_list.append(newMsg)
		print "msg is the first in the system\n"
		print newMsg
		print "\n\n"
		return 0

	else:	
		exist = 0	
		for msg in msg_list:
			print "listaca ", msg, "\ntodaslistas", msg_list
			msgHashId = msg._msg_hash
			newMsg.setMsgHash(msgHashId)
			if msg.__eq__(newMsg):
				exist = 1
				break

	if exist == 1:
		print "msg and newMsg are the same messages\n"
	else:
		print "msg and newMsg are different messages\n"
		hashid = HashTable.getHashId(newMsg._payload)
		newMsg.setMsgHash(hashid)
		msg_list.append(newMsg)
		print "hola ", newMsg

	print newMsg
	print "\n\n"
	return 0



if __name__ == "__main__":

	# Prepare the socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, sap.DEF_TTL)
	# Grab some info
	myaddr = socket.gethostbyname(socket.gethostname())

	msg_list = []
	HashTable = HashRegister()

	msg = sap.Message()
	msg.setSource(myaddr)
	msg.setPayload(SDP)
	msg.setMsgHash(0)
	print "el mensaje a chekear", msg
	check_msg(msg)
	del msg

	msg = sap.Message()
	msg.setSource(myaddr)
	msg.setPayload(SDP2)
	msg.setMsgHash(0)
	check_msg(msg)
	del msg

	msg = sap.Message()
	msg.setSource(myaddr)
	msg.setPayload(SDP3)
	msg.setMsgHash(0)
	check_msg(msg)
	del msg


	msg = sap.Message()
	msg.setSource(myaddr)
	msg.setPayload(SDP2)
	msg.setMsgHash(0)
	check_msg(msg)
	del msg

