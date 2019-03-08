

import sap
import socket
import time
import select
import struct
import datetime



###################################
##VARIABLES EXTRAIDAS DE GNURADIO##
###################################
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

command = "add"

msg = command + "\n" + SDP
#print command

def send_info():
    """ esto es para enviar un sap
    msg = sap.Message()
    msg.setSource(myaddr)
    msg.setPayload(SDP)
    msg.setMsgHash(1)
        data = msg.pack()
    """
    print "Sending packet"


    #sock_tx.connect(("",sap.DEF_PORT)) #TODO
    sock_tx.connect(("",4141)) #4141 puesto porque si


    #sock_tx.sendto(data, (sap.DEF_ADDR, sap.DEF_PORT)) # TODO
    #sock_tx.sendto(command + " " + data, (sap.DEF_ADDR, 4141)) # 4141 puesto porque si
    sock_tx.sendto(msg, (sap.DEF_ADDR, 4141)) # 4141 puesto porque si

if __name__ == "__main__":

    while True:
        sock_tx = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)  # SOCK_STREAM para tcp
        sock_tx.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        myaddr = socket.gethostbyname(socket.gethostname())
        try:
            send_info()
        except:
            print "No se ha podido conectar al servidor"
        time.sleep(5)
