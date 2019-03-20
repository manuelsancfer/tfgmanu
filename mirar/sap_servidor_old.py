import struct
from asyncore import poll

import sap
import socket
import time
import select
import struct
import datetime
import Queue


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
vic=IN IP4 224.2.17.12/127

t=2873397496 2873404696
a=recvonly
m=audio 49170 RTP/AVP 0
m=video 51372 RTP/AVP 31
m=application 32416 udp wb
a=orient:portrait"""

#######
##ADD##
#######
add_tx = "\nAnyadido"
SDP_add = """v=0
o=mhandley 2890844526 2890842807 IN IP4 126.16.64.4
s=SDP Seminar
protocolo: 
e=manu@manu (manu)
tipo de informacion:
hora inicio=
hora final=
frecuencia=
t=2873397496 2873404696
a=recvonly
m=audio 49170 RTP/AVP 0
m=video 51372 RTP/AVP 31
m=application 32416 udp wb
a=orient:portrait"""+ add_tx


###########
## DELETE##
###########

del_tx = "\Borrado"

SDP_delete = """v=0
o=mhandley 2890844526 2890842807 IN IP4 126.16.64.4
s=SDP Seminar
i=UDP"""

import time

# funcion para restar el time_out que queda, t2 es el tiempo actual
def timeturn(t1, t2):
    t= t1-t2
    print "e"
    print t
    date_str = int((t.microseconds + (t.seconds + t.days * 86400) * 10**6) / 10**6)
    print date_str
    return date_str

#funcion para enviar info de sesiones
def send_info():
    msg = sap.Message()
    msg.setSource(myaddr)
    msg.setPayload(SDP)
    msg.setMsgHash(1)
    print "Sending SAP packet"
    data = msg.pack()
    sock_tx.sendto(data, (sap.DEF_ADDR, sap.DEF_PORT))

if __name__ == "__main__":
    #########################
    ##RECEPCION DE DATOS TCP#
    #########################
    # Perpare the socket
    sock_rx_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)  # SOCK_STREAM para tcp
    sock_rx_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock_rx_tcp.bind(("", 4141)) # sap.DEF_PORT, 4141 puesto porque si
    sock_rx_tcp.listen(5)  # conexiones en cola
    mreq = struct.pack("4sl", socket.inet_aton(sap.DEF_ADDR), socket.INADDR_ANY)

    """
## Preprare the socket RX
	sock_rx = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP) #SOCK_STREAM para tcp
	sock_rx.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	#sock_rx.bind(("", sap.DEF_PORT))
	sock_rx.bind(("", 9875))	#conexion host, puerto
	sock_rx.listen(5) #conexiones en cola
	inputs = [sock_rx]
	outputs = []
	message_queues = {}
	mreq = struct.pack("4sl", socket.inet_aton(sap.DEF_ADDR), socket.INADDR_ANY)
	sock_rx.setsockopt(socket.SOL_SOCKET, socket.IP_TTL, mreq)	#SOL_SOCKET para tcp"""

    # TODO select

    ## Prepare the socket TX
    sock_tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock_tx.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, sap.DEF_TTL)
    # Grab some info TX
    myaddr = socket.gethostbyname(socket.gethostname())

    ##########################
    # conexion del receptor rx#
    ##########################



    while True:
        time_out = 8
        print "ves"

        connection_tcp, client_address_tcp = sock_rx_tcp.accept()
        print "true"

        try:
            data = connection_tcp.recv(4096)
            msg = sap.Message()
            try:
                msg.unpack(data)
            except:
                print "eeor"
            print "Received SAP TCP:\n", msg

        except socket.timeout, e: #socket o sock_rx_tcp

            err = e.args[0]
            if err == 'timed out':
                sleep(1)
                print 'recv timed out'
                continue
            else:
                print "er"
                #sys.exit(1)


        #server = socket_rx.socket(socket_rx.AF_INET, socket_rx.SOCK_STREAM)
	    #server.setblocking(0)
	    #server.bind(('localhost', 50000))	#conexion host, puerto
	    #server.listen(5)	#conexiones en cola
	    #inputs = [server]
	    #outputs = []
	    #message_queues = {}

	    ## esta parte seria del tcp
        inputs = [sock_rx_tcp]
        #inputs = [data]
        outputs = []
        message_queues = {}
        print "hola"

        readable, writable, exceptional = select.select(inputs, outputs, inputs, time_out=8)
        print "444"






        # tiempo actual+timeout
        time_finish_out = datetime.datetime.now() + datetime.timedelta(seconds=time_out)  # ira fuera
        print time_finish_out
        print time_out

        # print inputs

        # si el time out acaba se enviara la info de las sesiones
        if time_out == 8:
            print("holiwi")
            # Generate and send a message
            send_info()

        for s in readable:
            if s is sock_rx_tcp:

                connection, client_address = s.accept()
                connection.setblocking(0)
                inputs.append(connection)
                message_queues[connection] = Queue.Queue()
                print "2"

                # si el time_out no se ha pasado se continuara por donde deberia continuar
                if time_finish_out > datetime.datetime.now():
                    send_info()

                    time_out = timeturn(time_finish_out, datetime.datetime.now())
                    # si el time_out se ha pasado se enviara directamente
                else:

                    enviar = "TODO funcion"
            else:
                data = s.recv(1024)
                print "3"
                if data:
                    message_queues[s].put(data)
                    print "4"
                    if s not in outputs:
                        outputs.append(s)
                        print "5"
                else:
                    print "6"
                    if s in outputs:
                        outputs.remove(s)
                        print "7"
                    inputs.remove(s)
                    s.close()
                    del message_queues[s]

            if time_finish_out > datetime.datetime.now():
                send_info()
                time_out = timeturn(time_finish_out, datetime.datetime.now())
                # si el time_out se ha pasado se enviara directamente
            else:
                enviar = "TODO funcion"

        for s in writable:
            try:
                # next_msg = message_queues[s].get_nowait()
                print "8"
            except Queue.Empty:
                outputs.remove(s)
            else:
                # s.send(next_msg)
                print "9"
            if time_finish_out > datetime.datetime.now():
                send_info()

                time_out = timeturn(time_finish_out, datetime.datetime.now())
            # si el time_out se ha pasado se enviara directamente
            else:

                enviar = "TODO funcion"

        for s in exceptional:
            inputs.remove(s)
            print "10"
            if s in outputs:
                outputs.remove(s)
                print "9"
            s.close()
            del message_queues[s]
            if time_finish_out > datetime.datetime.now():
                send_info()
                time_out = timeturn(time_finish_out, datetime.datetime.now())
                # si el time_out se ha pasado se enviara directamente
            else:
                enviar = "TODO funcion"
















        """
# entrara cuando se acabe el timeout o entre un mensaje tcp (nueva conexion)
        while inputs:
            readable, writable, exceptional = select.select(
			    inputs, outputs, inputs, 2)
            print "444"

            # tiempo actual+timeout
            time_finish_out = datetime.datetime.now() + datetime.timedelta(seconds=time_out) #ira fuera
            print time_finish_out
            print time_out

            #print inputs

		    # si el time out acaba se enviara la info de las sesiones
            if time_out == 8:
                print("holiwi")
                # Generate and send a message
                send_info()


            for s in readable:
                if s is sock_rx_tcp:

                    connection, client_address = s.accept()
                    connection.setblocking(0)
                    inputs.append(connection)
                    message_queues[connection] = Queue.Queue()
                    print "2"


                    # si el time_out no se ha pasado se continuara por donde deberia continuar
                    if time_finish_out > datetime.datetime.now():
                        send_info()

                        time_out = timeturn(time_finish_out, datetime.datetime.now())
                        # si el time_out se ha pasado se enviara directamente
                    else:

                        enviar="TODO funcion"
                else:
                    data = s.recv(1024)
                    print "3"
                    if data:
                        message_queues[s].put(data)
                        print "4"
                        if s not in outputs:
                            outputs.append(s)
                            print "5"
                    else:
                        print "6"
                        if s in outputs:
                            outputs.remove(s)
                            print "7"
                        inputs.remove(s)
                        s.close()
                        del message_queues[s]

                if time_finish_out > datetime.datetime.now():
                    send_info()
                    time_out = timeturn(time_finish_out, datetime.datetime.now())
                    # si el time_out se ha pasado se enviara directamente
                else:
                    enviar = "TODO funcion"

            for s in writable:
			    try:
				    #next_msg = message_queues[s].get_nowait()
				    print "8"
			    except Queue.Empty:
				    outputs.remove(s)
			    else:
				    #s.send(next_msg)
				    print "9"
			    if time_finish_out > datetime.datetime.now():
				    send_info()

				    time_out = timeturn(time_finish_out, datetime.datetime.now())
			    # si el time_out se ha pasado se enviara directamente
			    else:

				    enviar = "TODO funcion"

            for s in exceptional:
                inputs.remove(s)
                print "10"
                if s in outputs:
                    outputs.remove(s)
                    print "9"
                s.close()
                del message_queues[s]
                if time_finish_out > datetime.datetime.now():
                    send_info()
                    time_out = timeturn(time_finish_out, datetime.datetime.now())
                    # si el time_out se ha pasado se enviara directamente
                else:
                    enviar = "TODO funcion
            """