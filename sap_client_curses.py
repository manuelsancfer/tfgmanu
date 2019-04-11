import sys, os
import curses
import select
import time
import sap
import socket
import struct

from SDP import *
from panel import *
from SatRegister import *

sapdebug = 0

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

    SatReg = SatRegister()
    if (sapdebug != 1):
        SatPanel = Panel(SatReg)
        SatPanel.drawMainPanel('Main Panel')

    while True:
        try:

            inputs = [sock, sys.stdin]

            outputs = []
            message_queues = {}

            readable, writable, exceptional = select.select(inputs, [], [], garbage_collector_period)
            # print "Event"
            if len(readable) != 0:
                # Check if socket is ready to be read
                if sock in readable:
                    # print "Reading socket"
                    data = sock.recv(4096)
                    msg = sap.Message()
                    msg.unpack(data)
                    sdp_parser = SDPParser(msg._payload.splitlines())
                    sdp_parser.run()
                    # print sdp_parser.outbox
                    SdpSatSession = SDPSession(sdp_parser.outbox)
                    # print SdpSatSession
                    for k, SdpSatObj in SatReg._SatRegister.items():
                        # print SdpSatSession.__eq__(SdpSatObj)
                        # print "Dump of SdpSatObj numb %d" % k
                        # print SdpSatObj
                        if SdpSatObj == SdpSatSession:
                            if msg._deletion:
                                SatReg.del_satellite(SdpSatObj)
                                if (sapdebug != 1):
                                    SatPanel.drawMainPanel("Main Panel")
                                else:
                                    print SatReg._SatRegister
                                continue
                            else:
                                # We have received a SAP for an existing SDP Sat Session
                                # update timestamp in this SDPSatObj:
                                SdpSatObj.setLast_timestamp(time.time())
                                continue
                    # Here, we have a SAP for an unexising SDP Sat Session
                    if msg._deletion:
                        continue
                    SdpSatSession.setLast_timestamp(time.time())
                    SatReg.add_satellite(SdpSatSession)
                    if (sapdebug != 1):
                        SatPanel.drawMainPanel("Main Panel")
                    else:
                        print SatReg._SatRegister
                    del SdpSatSession

                # Check if keyboard is has a keypressed waiting to be read
                if sys.stdin in readable:
                    if (sapdebug != 1):
                        k = SatPanel.wobj.getch()
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
                                SatPanel.StatusInfo("Satellite idx %s" % (k - 48))
                                SatPanel.drawInfoPanel(k - 48)
                        # If we are showing Satellite Details Panel, then go back to the MainPanel
                        elif SatPanel.active == SatPanel._InfoPanel:
                            SatPanel.drawMainPanel("Main Panel")
                    else:
                        pass

                # print "time out "
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

        except Exception as e:
            if (sapdebug != 1):
                if SatPanel.active == SatPanel._MainPanel:
                    SatPanel.drawMainPanel("Main Panel")
                elif SatPanel.active == SatPanel._InfoPanel:
                    SatPanel.drawInfoPanel(SatPanel._InfoPanel)
            else:
                print(e)


if __name__ == "__main__":
    main()

