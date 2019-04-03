import curses
import select
import time
import sap
import socket
import struct



from SDP import *
from panel import *
from SatRegister import *

sapdebug=0

msg_list = []
dictionary = {}




msg_list = []
dictionary = {}

def main():

	# Prepare the socket


	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind(("", sap.DEF_PORT))
	mreq = struct.pack("4sl", socket.inet_aton(sap.DEF_ADDR), socket.INADDR_ANY)
	sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

	garbage_collector_period = 5


	#a.print_satellites()
	SatReg = SatRegister()
	if (sapdebug != 1):
		SatPanel = Panel(SatReg)
		SatPanel.drawMainPanel('Main Panel')

	while True:

		inputs = [sock, sys.stdin]

		outputs = []
		message_queues = {}

		readable, writable, exceptional = select.select(inputs, [], [], garbage_collector_period)

		if len(readable)!=0:
			if sock in readable:
				data = sock.recv(4096)
				msg = sap.Message()
				msg.unpack(data)
				"""
				sdp_parser = SDPParser(msg._payload.splitlines())
				sdp_parser.run()"""

				sdp = ""
				# se quita el primero porque sobra, y los dos ultimos porque llegan vacios
				print (len(data.split('\n')))
				for i in range(1, len(data.split('\n'))-2):
					sdp = sdp + data.split('\n')[i] + "\n"
				sdp_parser = SDPParser(sdp.splitlines())
				sdp_parser.run()
				SdpSatSession = SDPSession(sdp_parser.outbox)




			if len(msg_list) == 0:

				SdpSatSession.setLast_timestamp(time.time())
				SatReg.add_satellite(SdpSatSession)
				msg.setLast_timestamp(time.time()) #todo ver si son necesarios los dos
				msg_list.append(msg)

				if (sapdebug != 1):
					SatPanel.drawMainPanel("Main Panel")
				else:
					print SatReg._SatRegister
				del SdpSatSession


			else:
				#se comprueba si existe el mensaje
				exist = False

				for k, SdpSatObj in SatReg._SatRegister.items():
					if SdpSatObj == SdpSatSession:
						# si existe el mensaje no se anyadira
						exist = True
						"""
						if ms.__eq2__(msg):
							# si existe un mensaje igual se retorna un 1
							print "Es un mensaje igual, no actuaria"
							# todo probar si borra"""

						if SdpSatObj == SdpSatSession:
							if msg._deletion:


								SatReg.del_satellite(SdpSatObj)
								print "Esta marcado el delete, se borra"

								for ms in msg_list: #todo comprobar si se puede hacer sin esto
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
								for ms in msg_list: #todo comprobar si se puede hacer sin esto
									if ms == msg:
										ms.setLast_timestamp(time.time())

								SdpSatObj.setLast_timestamp(time.time())
								continue
						#else:
							"""
							print "Esta marcado el delete, se borra"
							msg_list.remove(ms)
							# todo probar si borra
							"""
							"""sdp_parser = SDPParser(newMsg)
							sdp_parser.run()
							sdpsession1 = SDPSession(sdp_parser.outbox)
							a.del_satellite(sdpsession1)"""
							"""sdp_parser = SDPParser(newMsg)
							sdp_parser.run()
							sdpsession1 = SDPSession(sdp_parser.outbox)
							if SDPSession.__eq__(sdpsession1):
							#for i in a.satellite_register:
								#if a.satellite_register[i]
								#if a.satellite_register[i] == sdpsession1:
									SDPSessionObj = a.satellite_register[i]
									a.del_satellite(SDPSessionObj)
									a.drawMainPanel("MainPanel")
								break
							#a.add_satellite(sdpsession1)
							a.drawMainPanel("MainPanel")


							break"""

				if exist == False:
					# si no existe ningun paquete igual se anyade
					print "Mensaje anyadido"


					SdpSatSession.setLast_timestamp(time.time())
					SatReg.add_satellite(SdpSatSession)

					if (sapdebug != 1):
						SatPanel.drawMainPanel("Main Panel")
					else:
						print SatReg._SatRegister
					del SdpSatSession

					msg.setLast_timestamp(time.time())
					msg_list.append(msg)

					"""
					sdp_parser = SDPParser(newMsg)
					sdp_parser.run()
					sdpsession1 = SDPSession(sdp_parser.outbox)
					a.add_satellite(sdpsession1)
					a.drawMainPanel("MainPanel")

					msg.setLast_timestamp(time.time())
					"""

			print "Ready"
			print "longitud lista", len(msg_list)



		if not (readable or writable):
			print "time out "
			for ms in msg_list:
				# mira si hay que borrar algun paquete
				print "dentro del borra de timeout"
				delete = ms.intervalPacket(time.time())
				if delete == 1:
					print "borrado del "
					# si devuelve 1 borara el paquete
					msg_list.remove(ms)
					if (sapdebug != 1):
						SatPanel.drawMainPanel("Main Panel")
				else:
					print "no se borra"
				print "longitud lista es ", len(msg_list)


			for SdpSatObj in SatReg._SatRegister.values():
				# mira si hay que borrar algun paquete
				# print "dentro del borra de timeout"
				delete = SdpSatObj.intervalPacket(time.time())
				if delete == 1:
					# print "borrado del "
					# si devuelve 1 borara el paquete
					SatReg.del_satellite(SdpSatObj)
					if (sapdebug != 1):
						SatPanel.drawMainPanel("Main Panel")

				else:
					pass
			# print "no se borra"

		#inputs = [sys.stdin]
		"""try:
			k = a.wobj.getch()
			if k == ord('q'):
				curses.endwin()
				break
			if a.active == a._MainPanel:
				maxsats = len(a.satellite_register)
				if (k-48) > -1 and (k-48) < maxsats :
					a.drawInfoPanel(k-48)
				elif a.active == a._InfoPanel:
					a.drawMainPanel()"""

		"""except:
			
            if a.active == a._MainPanel:
                a.drawMainPanel()
            elif a.active == a._InfoPanel:
                a.drawInfoPanel(a._InfoPanel)
			e=3 """



if __name__ == "__main__":
	main()

