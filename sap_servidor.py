import struct
from asyncore import poll

import sap
import socket
import time
import select
import struct
import datetime
import Queue
import time
import string


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
def Add_Hash(hash_id=0): # TODO implementar poder devolver error
    # todo
    for i in range(0, pow(2, 16)+1):
        if Msg_Lista[i] == "No disponible":
            # sino esta disponible el programa debe continuar
            continue

        else:
            # ponemos en la lista que ese numero de hash no esta disponible
            Msg_Lista.update({i:'No disponible'})
            hash_id = i
            break

    if (hash_id != 0):
        return hash_id

    else:
        print ("No hay ninguna conexion disponible.")
        # implementar return error

def Delete_Hash(hash_id):
    # Actualizamos el valor del hash id poniendolo disponible
    Msg_Lista.update({hash_id:'Disponible'})
    # todo avisar al cliente que se ha borrado



def New_message_rx():
    """
    Mensaje={}
    Mensaje2={}

    print "Nuevo mensaje:"
    print msg
    print "pack:"
    print type(msg)
    # convertimos a string el mensaje
    msg_str=str(msg)
    # troceamos el mensaje y escogemos la tercera parte que sera la que contenga el mensaje
    gnu=msg_str.split("\n")[3]
    # troceamos esta parte del mensaje y la guardamos en variables
    gnu2=gnu.split("\\n")
    gnu_hora_inicio = ""
    gnu_hora_fin = ""
    gnu_ancho_banda = ""
    gnu_frecuencia = ""
    Mensaje.update({'gnu_mail': gnu2[5]})
    gnu_cmd = ""
    Mensaje.update({'gnu_protocolo': gnu2[12]})
    print "protocolo:"
    print gnu_protocolo
    print "el mensaje protocolo:"
    print Mensaje.get('gnu_protocolo')
    print "fin"
    Mensaje2={'id1': Mensaje, 'id2':Mensaje}
    print "mensaje 2: de protoclo"
    print Mensaje2.get('id2').get('gnu_protocolo')
    print "fin del to"
    gnu_info = ""
    gnu_ip = ""
    gnu_puerto = ""
    gnu_tipo_datos = ""
    gnu_satelite = ""

    SDP=gnu_protocolo + "\n" + gnu_mail """

    #newMsg = sap.Message()
    #newMsg.setSource(myaddr) # mete la direccion
    #newMsg.setPayload(SDP) #mete el payload
    #newMsg.setMsgHash(0) # deberia meter un hash aleatorio, asi mete un 0


    msg = None
    for msg in Msg_Lista:
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
        Msg_Lista.append(newMsg)
    else:
        # El SDP recibido por el socket ya existe en el sistema
        # en este punto del programa newMsg y msg son iguales
        # TODO modificar o borrar el mensaje
        print ""

if __name__ == "__main__":

    # Lista para los hash
    Msg_Lista = {}
    # Rellenamos la lista
    for i in range(0, pow(2, 16) + 1):
        Msg_Lista.update({i: 'Disponible'})


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

    time_out=8 # TODO hay que cambiarlo

    while True:
        print "True"

        readable, writable, exceptional = select.select(inputs, inputs, [], time_out)
        print "Select"

        ## Si entran datos:
        if len(readable) != 0:
            # Aceptaremos la conexion
            connection_tcp, client_address_tcp = sock_rx_tcp.accept()

            try:
                # RECOGIDA DE DATOS
                data = connection_tcp.recv(4096)
                #msg = sap.Message()
                # RECOGIDA DEL COMANDO
                comando = data.split('\n')[0]
                # RECOGIDA DEL PAYLOAD (PARTE DEL SDP)
                sdp = ""
                print (len(data.split('\n')))
                for i in range(1, len(data.split('\n'))):
                    sdp = sdp + data.split('\n')[i] + "\n"

                #try:
                    #msg.unpack(data)
                #except:
                    #print "error"
                # mostramos los datos

                print "Received SAP TCP:\n", sdp
                # TODO BORRAR ESTS DOS LINEAS DE ABAJO
                #New_message_rx()

                if comando == "add":
                    print""
                    hash_id = Add_Hash()
                elif comando == "delete":
                    print ""
                    # Delete_Hash() todo bien
                else:
                    print "El comando no es correcto."

                print datetime.datetime.now()


            except socket.timeout, e:  # socket o sock_rx_tcp

                err = e.args[0]
                if err == 'timed out':
                    sleep(1)
                    print 'recv timed out'
                    continue
                else:
                    print "er"
                    # sys.exit(1)

                inputs = [sock_rx_tcp]
                outputs = []
                message_queues = {}

        # tiempo actual+timeout
        time_finish_out = datetime.datetime.now() + datetime.timedelta(seconds=time_out)  # ira fuera
        print "el tiempo final es:"
        print time_finish_out
        print "el time out es "
        print time_out

        # print inputs

        for s in readable:
            if s is sock_rx_tcp:

                connection, client_address = s.accept()
                #connection.setblocking(0)
                inputs.append(connection)
                message_queues[connection] = Queue.Queue()
                print "2"

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


        for s in exceptional:
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
                send_info()

        if not (readable or writable or exceptional):
            # timeout
            print "timeout agotado"
            send_info()
            time_out=8















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