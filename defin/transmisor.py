#!/usr/bin/env python

# import libraries
import sap
import socket
import time


####################################
##VARIABLES EXTRACTED FROM GNURADIO#
####################################
gnu_hora_inicio= ""
gnu_hora_fin= ""
gnu_ancho_banda= ""
gnu_frecuencia= ""
gnu_mail= ""
gnu_cmd= ""
gnu_protocolo= ""
gnu_info= ""
gnu_ip= ""
gnu_puerto= ""
gnu_tipo_datos= ""
gnu_satelite= ""

SDP = """\

v=0
o=mhandley 2890844526 2890842807 IN IP4 tgs.upc.edu
s=OSCAR-7i
i=OSCAR-7 data multicasting
u=http://tgs.upc.edu/oscar7
e=mjh@isi.edu (Mark Handley)
c=IN IP4 239.10.10.9/127
t=1552557431 1552558031
a=recvonly
m=application 5500 udp GNURadio
a=BkName: USRP Source
a=SampleFmt: Complex
a=SampleRate: 6.25Msps
a=Carrier:1.961GHz
a=Antenna Gain: 25dB
"""


SDP_ = """\

v=0
o=mhandley 2890844526 2890842807 IN IP4 tgs.upc.edu
s=OSCAR-7i
i=OSCAR-7 data multicasting
u=http://tgs.upc.edu/oscar7
e=mjh@isi.edu (Mark Handley)
c=IN IP4 239.10.10.9/127
t=1552557431 1552558031
a=recvonly
m=application 5500 udp GNURadio
a=BkName: USRP Source
a=SampleFmt: Complex
a=SampleRate: 6.25Msps
a=Carrier:1.961GHz
a=Antenna Gain: 25dB
"""

SDP2 = """\

v=0
o=mhandley 1345678931 1838482808 IN IP4 tgs.upc.edu
s=ISS
i=ISS data multicasting
u=http://tgs.upc.edu/iss
e=mjh@isi.edu (Mark Handley)
c=IN IP4 239.10.10.10/127
t=1552562431 1552563031
a=recvonly
m=application 5000 udp GNURadio
a=BkName: USRP Source
a=SampleFmt: Complex
a=SampleRate: 6.25Msps
a=Carrier:1.951GHz
a=Antenna Gain: 25dB
"""



SDP3 = """\

v=0
o=mhandley 4000441234 401032110 IN IP4 tgs.upc.edu
s=HUBBLE
i=HUBBLE data multicasting
u=http://tgs.upc.edu/hubble
e=mjh@isi.edu (Mark Handley)
c=IN IP4 239.10.10.12/127
t=1552565431 1552566031
a=recvonly
m=application 4500 udp GNURadio
a=BkName: USRP Source
a=SampleFmt: Complex
a=SampleRate: 6.25Msps
a=Carrier:1.931GHz
a=Antenna Gain: 25dB
"""

###############################
##EXAMPLE TO SEND SAP PACKETS##
###############################

command = "add"
command2 = "delete"

msg_lista = []

msg_lista.append(command + "\n" + SDP)
msg_lista.append(command + "\n" + SDP2)
msg_lista.append(command + "\n" + SDP3)
msg_lista.append(command2 + "\n" + SDP2)


def send_info(NewMsg):
    """
    Function to send sap messages through TCP.
    """

    print "Sending packet"
    sock_tx.connect(("",4141)) #todo poner puerto

    sock_tx.sendto(NewMsg, (sap.DEF_ADDR, 4141)) # todo poner puerto
    answer = sock_tx.recv(4096)
    print answer

if __name__ == "__main__":
    while True:

        for msg in msg_lista:
            # prepare socket conection
            sock_tx = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)  # SOCK_STREAM para tcp
            sock_tx.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            myaddr = socket.gethostbyname(socket.gethostname())

            try:
                send_info(msg)
                print "Sent the package\n", msg
            except:
                print "Unable to connect to server"
            time.sleep(4)
        print "All packages have been sent"
        time.sleep(1) # todo cada cuanto envia

