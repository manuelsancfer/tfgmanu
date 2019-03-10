import struct
from asyncore import poll

import sap
import socket
import time
import select
import struct
import datetime
import Queue
import string
import sap_gnuradio


# PYTHON NCOURSES
# 2^16 HASH

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



# funcion para restar el time_out que queda, t2 es el tiempo actual
def timeturn(t1, t2):
    t= t1-t2
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


#Lista_TX={}
# Variable diccionario

# funcion que asigna un nuevo hash
def Add_Hash(): # TODO implementar poder devolver error

    disponible = False
    for i in range(0, pow(2, 16)+1):
        if Msg_Hash[i] == "No disponible":
            # sino esta disponible el programa debe continuar
            continue

        else:
            # ponemos en la lista que ese numero de hash no esta disponible
            Msg_Hash.update({i:'No disponible'})
            hash_id = i
            disponible = True
            break

    if (disponible == True):
        return hash_id

    else:
        print ("No hay ninguna conexion disponible.")

def Delete_Hash(hash_id):
    # Actualizamos el valor del hash id poniendolo disponible
    Msg_Hash.update({hash_id:'Disponible'})
    # todo avisar al cliente que se ha borrado


def check_msg(payload, comando):
    Newmsg = sap.Message()
    Newmsg.setPayload(payload)

    # comprobamos si existe algun mensaje igual
    for msg in msg_list:
        msgHashId = msg._msg_hash
        Newmsg.setSource(myaddr)
        Newmsg.setMsgHash(msgHashId)

        if msg.__eq__(Newmsg):
            # si existe un mensaje igual se retorna un 1
            if comando == "add":
                return 1
            else:
                return 1, msgHashId, msg
    # sino ha encontondrado un mensaje igual se retorna un 0
    if comando == "add":
        return 0
    else:
        return 0, "", ""

#msg_list = []
def New_message_rx(data):
    global msg_list

    Newmsg = sap.Message()

    comando = data.split('\n')[0]
    # RECOGIDA DEL PAYLOAD (PARTE DEL SDP)
    sdp = ""
    print (len(data.split('\n')))
    for i in range(1, len(data.split('\n'))):
        sdp = sdp + data.split('\n')[i] + "\n"

    if comando == "add":

        if len(msg_list) == 0:
            # si la lista esta vacia anyadimos un hash
            hashid = Add_Hash()
            Newmsg.setSource(myaddr)
            Newmsg.setPayload(sdp)
            Newmsg.setMsgHash(hashid)
            print "msg is the first in the system\n"
            print Newmsg
            print "\n\n"
            msg_list.append(Newmsg)
            del Newmsg

            # retornanos un 1 para recalcular el tiempo
            return 1
        else:
            # Comprobamos si el sdp ya existe
            existe = check_msg(sdp, comando) # TODO VER SI FALLA POR DEVOLVER DOS COSAS

            if existe == 1:
                print "msg and newMsg are the same messages\n"
            else:
                print "msg and newMsg are different messages\n"
                hashid = Add_Hash()

                if hashid == "No hay ninguna conexion disponible.":
                    print hashid
                    del Newmsg
                else:
                    Newmsg.setSource(myaddr)
                    Newmsg.setPayload(sdp)
                    Newmsg.setMsgHash(hashid)
                    # data = Newmsg.pack() todo mirar pero creo que fuera
                    msg_list.append(Newmsg)
                    del Newmsg

                    # retornanos un 1 para recalcular el tiempo
                    return 1

    elif comando == "delete":
        if comando == "add":

            if len(msg_list) == 0:
                # si la lista esta vacia no hacemos nada
                print "No hay ningun mensaje en la lista"
                del Newmsg

            else:
                # comprobamos si existe algun mensaje igual
                existe, hashid, msg = check_msg(sdp, comando)
                if existe == 0:
                    # si no existe ningun mensaje igual no hacemos nada
                    print "No existe ningun mensaje igual que Newmsg\n"
                else:
                    print "Se ha borrado el mensaje.\n"
                    Delete_Hash(hashid)
                    msg_list.remove(msg)
                del Newmsg


    else:
        print "El comando no es correcto."
        del Newmsg
    return 0

"""
    msg = None
    for msg in Msg_Hash:
        hasid = msg._msg_hash
        print "el hasid de momento es"
        print hasid
        newMsg.setMsgHash(hasid)
        if msg.__eq__(newMsg):
            # newMsg y msg son iguales
            break
    print "el msg"
    if msg == None:
        print "dentro del None"
        # El mensaje SDP es nuevo
        # Si hay que enviar este nuevo mensaje, hay que asignar un nuevo hashid que no este en uso
        #hasid = get_New_HasId(newMsg)
        #hasid = newMsg.unpack(data)

        newMsg.setMsgHash(hasid)
        # Anyadir nuevo mensaje a la lista de mesnajes
        Msg_Hash.append(newMsg)
    else:
        # El SDP recibido por el socket ya existe en el sistema
        # en este punto del programa newMsg y msg son iguales
        # TODO modificar o borrar el mensaje
        print """

def Recalcular(time_out=0, time_finish_out=0):
    sumatorio = 0

    for m in msg_list:
        # necesitamos empaquetar el mensaje para ver cuanto ocupa y recalcular el time_out
        data = m.pack()
        sumatorio = sumatorio + len(data)
    time_out_new = sap.tx_delay(sumatorio/len(msg_list))

    if (time_out == 0):
        return time_out_new

    else:
        dif_time = time_out_new - time_out
        time_finish_out = time_finish_out + datetime.timedelta(seconds=dif_time)
        return time_out_new, time_finish_out


if __name__ == "__main__":

    # Lista para los hash
    Msg_Hash = {}
    # Rellenamos la lista
    for i in range(0, pow(2, 16) + 1):
        Msg_Hash.update({i: 'Disponible'})
    msg_list = []

    ##########################
    ##RECEPCION DE DATOS TCP##
    ##########################
    # Perpare the socket RX
    sock_rx_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)  # SOCK_STREAM para tcp
    sock_rx_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock_rx_tcp.bind(("", 4141)) # sap.DEF_PORT, 4141 puesto porque si
    sock_rx_tcp.listen(5)  # conexiones en cola
    mreq = struct.pack("4sl", socket.inet_aton(sap.DEF_ADDR), socket.INADDR_ANY)

    inputs = [sock_rx_tcp]
    outputs = []
    message_queues = {}

    #######################
    ##TRANSMISOR DE DATOS##
    #######################
    ## Prepare the socket TX
    sock_tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock_tx.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, sap.DEF_TTL)
    # Grab some info TX
    myaddr = socket.gethostbyname(socket.gethostname())

    time_principio = datetime.datetime.now()
    time_out=8 # TODO hay que cambiarlo

    while True:


        readable, writable, exceptional = select.select(inputs, inputs, [], time_out)

        time_hasta_ahora = (datetime.datetime.now()-time_principio).seconds
        time_finish_out = datetime.datetime.now() + datetime.timedelta(seconds=time_hasta_ahora)
        # Envio permite saber si el time_out ya ha acabado
        envio = False

        ## Si entran datos:
        if len(readable) != 0:
            # Aceptaremos la conexion
            connection_tcp, client_address_tcp = sock_rx_tcp.accept()

            try:
                # RECOGIDA DE DATOS
                data = connection_tcp.recv(4096)
                #msg = sap.Message()
                # RECOGIDA DEL COMANDO


                #try:
                    #msg.unpack(data)
                #except:
                    #print "error"
                # mostramos los datos

                print "Received SAP TCP:\n"
                # Lo guardamos en recalcular para saber si hay que recalcular el tiempo
                recalcular = New_message_rx(data)
                print datetime.datetime.now()

                if recalcular == 1:
                    # si recalcular es 1 hay que recalcular el tiempo anyadido en time_out
                    # y cuando tenemos que enviar el tcp(time_finish_out)
                    time_out, time_finish_out = Recalcular(time_out, time_finish_out)

                # si el tiempo actual es mas grande que el tiempo donde tenia que haber terminado se marca
                # para enviar el tcp, sino se recalcula el tiempo que falta(time_out)
                if time_finish_out > datetime.datetime.now():

                    time_out = timeturn(time_finish_out, datetime.datetime.now())
                    # si el time_out se ha pasado se enviara directamente
                else:
                    envio = True



            except socket.timeout, e:  # socket o sock_rx_tcp

                err = e.args[0]
                if err == 'timed out':
                    print 'recv timed out'
                    continue
                else:
                    print "er"
                    # sys.exit(1)

                inputs = [sock_rx_tcp]
                outputs = []
                message_queues = {}


        """for s in readable:
            if s is sock_rx_tcp:

                connection, client_address = s.accept()
                inputs.append(connection)
                message_queues[connection] = Queue.Queue()

                # si el time_out no se ha pasado se continuara por donde deberia continuar
                if time_finish_out > datetime.datetime.now():

                    time_out = timeturn(time_finish_out, datetime.datetime.now())
                    # si el time_out se ha pasado se enviara directamente
                else:
                    send_info()

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
                    inputs.remove(s) # TODO tcp close
                    s.close()
                    del message_queues[s]

            if time_finish_out > datetime.datetime.now():

                time_out = timeturn(time_finish_out, datetime.datetime.now())
                # si el time_out se ha pasado se enviara directamente
            else:
                send_info()
                enviar = "TODO funcion"
                """

        """for s in writable:
            try:
                # next_msg = message_queues[s].get_nowait()
                print "8"
            except Queue.Empty:
                outputs.remove(s)
            else:
                # s.send(next_msg)
                print "9"
            if time_finish_out > datetime.datetime.now():


                time_out = timeturn(time_finish_out, datetime.datetime.now())
            # si el time_out se ha pasado se enviara directamente
            else:
                send_info()
                print "aqui"
                time_out=8"""


        """for s in exceptional:
            inputs.remove(s)
            print "10"
            if s in outputs:
                outputs.remove(s)
                print "9"
            s.close()
            del message_queues[s]
            if time_finish_out > datetime.datetime.now():

                time_out = timeturn(time_finish_out, datetime.datetime.now())
                # si el time_out se ha pasado se enviara directamente
            else:
                send_info()"""


        if not (readable or writable or exceptional or envio==True):
            # timeout
            print "timeout agotado"

            if len(msg_list) != 0:
                send_info()
                time_out = Recalcular()
                print time_out

            else:
                print "No hay ningun paquete para enviar. \n"
                print time_out















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