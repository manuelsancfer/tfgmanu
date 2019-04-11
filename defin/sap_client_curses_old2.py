
# import libraries
import sap
import socket
import struct

# import from other scripts
from panel import *
from SatRegister import *

# todo poner quees este debug
sapdebug=0

msg_list = []
dictionary = {}

def main():

	# Prepare the socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind(("", sap.DEF_PORT))
	mreq = struct.pack("4sl", socket.inet_aton(sap.DEF_ADDR), socket.INADDR_ANY)
	sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

	# todo  poner que es este tiempo
	garbage_collector_period = 5

	# initialize the satellite registry
	SatReg = SatRegister()

	if (sapdebug != 1):
		SatPanel = Panel(SatReg)
		SatPanel.drawMainPanel('Main Panel')

	while True:

		inputs = [sock, sys.stdin]

		# select will wake up when data enters or the garbage_collector_period runs out
		readable, writable, exceptional = select.select(inputs, [], [], garbage_collector_period)

		if len(readable)!=0:

			# if there is keyboard input
			if sys.stdin in readable:
				if (sapdebug != 1):
					k = SatPanel.wobj.getch()
					# with the q key, go back
					if k == ord('q'):
						curses.endwin()
						break

					# Check if we are showing the mainPanel with the summary list of satellites
					if SatPanel.active == SatPanel._MainPanel:
						maxsats = len(SatReg._SatRegister)
						# Check if key ascii code is in the range from '0' (ascii 48) to ascii maxsats + 48:
						# In other words ... check if keypressed a number between 0  and maxsats-1
						if (k - 48) > -1 and (k - 48) < maxsats:
							# Display Detailed information of satellite indexed by the keypressed
							SatPanel.StatusInfo("Satellite idx %s" % (k-48))
							SatPanel.drawInfoPanel(k-48)

					# If we are showing Satellite Details Panel, then go back to the MainPanel
					elif SatPanel.active == SatPanel._InfoPanel:
						SatPanel.drawMainPanel("Main Panel")
				else:
					pass
				continue

			# if the data that comes in comes from the socket
			if sock in readable:
				data = sock.recv(4096)
				msg = sap.Message()
				msg.unpack(data)

				# build the sdp package
				sdp = ""
				for i in range(1, len(data.split('\n'))-2):
					sdp = sdp + data.split('\n')[i] + "\n"
				sdp_parser = SDPParser(sdp.splitlines())
				sdp_parser.run()
				SdpSatSession = SDPSession(sdp_parser.outbox)


			if len(msg_list) == 0:

				# point to the last hour the package arrived in sdp
				SdpSatSession.setLast_timestamp(time.time())
				# add the sdp to the list of satellites
				SatReg.add_satellite(SdpSatSession)
				# point to the last hour the package arrived in message
				msg.setLast_timestamp(time.time())
				msg_list.append(msg)

				if (sapdebug != 1):
					SatPanel.drawMainPanel("Main Panel")
				else:
					print SatReg._SatRegister
				del SdpSatSession


			else:
				# to check if the message exists
				exist = False

				for k, SdpSatObj in SatReg._SatRegister.items():
					# check if the message exists, then the message is not added
					if SdpSatObj == SdpSatSession:
						exist = True

						if SdpSatObj == SdpSatSession:
							# check if the message is marked for deletion
							if msg._deletion:
								SatReg.del_satellite(SdpSatObj)

								for ms in msg_list:
									if ms == msg:
										msg_list.remove(ms)

								if (sapdebug != 1):
									SatPanel.drawMainPanel("Main Panel")

								else:
									print SatReg._SatRegister
								continue

							else:
								# We have received a SAP for an existing SDP Sat Session
								# update timestamp in this SDPSatObj:
								for ms in msg_list:
									if ms == msg:
										ms.setLast_timestamp(time.time())

								SdpSatObj.setLast_timestamp(time.time())
								continue

				if exist == False:
					# add the message

					SdpSatSession.setLast_timestamp(time.time())
					SatReg.add_satellite(SdpSatSession)

					if (sapdebug != 1):
						SatPanel.drawMainPanel("Main Panel")

					else:
						print SatReg._SatRegister
					del SdpSatSession

					msg.setLast_timestamp(time.time())
					msg_list.append(msg)

		# if in select garbage_collector_period is over
		if not (readable or writable):
			# check if you have to delete a satellite if it has not been
			# received in the stipulated time
			for ms in msg_list:
				delete = ms.intervalPacket(time.time())
				if delete == 1:
					msg_list.remove(ms)

					if (sapdebug != 1):
						SatPanel.drawMainPanel("Main Panel")
				else:
					pass

			# check if you have to delete a satellite if it has not been
			# received in the stipulated time
			for SdpSatObj in SatReg._SatRegister.values():

				delete = SdpSatObj.intervalPacket(time.time())
				if delete == 1:
					SatReg.del_satellite(SdpSatObj)

					if (sapdebug != 1):
						SatPanel.drawMainPanel("Main Panel")

				else:
					pass

		#inputs = [sys.stdin]


if __name__ == "__main__":
	main()

