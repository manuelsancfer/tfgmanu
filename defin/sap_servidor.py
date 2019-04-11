#!/usr/bin/env python
# Author Manuel Sanchez Fernandez
"""For receive sap messages and transmitting sdp messages
to multicast groups
"""

# import the libraries
import sap
import socket
import select
import struct
import datetime

###########################
##VARIABLES FROM GNURADIO##
###########################
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



def timeturn(t1, t2):
    """
    Return returns the remaining timeout time.
    :param t1: time when it should end
    :param t2: actual time
    :return:
    """
    t= t1-t2
    date_str = int((t.microseconds + (t.seconds + t.days * 86400) * 10**6) / 10**6)
    print date_str
    return date_str

def send_info(command="add", msg_delete=""):
    """
    function to send the information of sessions.
    :param command: add by defect or delete.
    :param msg_delete: if command=add then in this function we will build the sap packet;
        else the sap packet comes built.
    """

    if command == "delete":
        print "Sending delete SAP packet"
        sock_tx.sendto(msg_delete, (sap.DEF_ADDR, sap.DEF_PORT)) #todo mirar si esta bien el envio

    else:
        for msg in msg_list:
            print "Sending SAP packet"
            data = msg.pack()
            sock_tx.sendto(data, (sap.DEF_ADDR, sap.DEF_PORT))

def add_hash():
    """
    Function to assign a new Hash value
    """

    available = False
    for i in range(0, pow(2, 16)+1):
        if Msg_Hash[i] == "Not available":
            continue

        else:
            Msg_Hash.update({i:'Not available'})
            hash_id = i
            available = True
            break

    if (available == True):
        return hash_id

    else:
        print ("There is no connection available.")

def Delete_Hash(hash_id, msg):
    """
    Function to free Hash value when there is an implicit delete
    :param hash_id: hash value from message to delete
    :param msg: message to delete
    """
    msg.setDeletion(True)
    data = msg.pack()
    send_info("delete", data)
    msg_list.remove(msg)
    Msg_Hash.update({hash_id:'Available'})

def check_msg(payload, command):
    """
    Function to check if the message exists(1) or not(0).
    And if the command is delete it also returns the hash value and the message
    :param payload: payload sap message
    :param command: command can be add or delete
    :return:
    """

    Newmsg = sap.Message()
    Newmsg.setPayload(payload)

    # check if the message exists or not
    for msg in msg_list:
        msgHashId = msg._msg_hash
        Newmsg.setSource(myaddr)
        Newmsg.setMsgHash(msgHashId)

        if msg.__eq__(Newmsg):
            if command == "add":
                return 1
            else:
                return 1, msgHashId, msg

    if command == "add":
        return 0
    else:
        return 0, "", ""

def tcp_handler(data):
    """
    Function to handle the sap package. Separates the command from the sap,
    with the command choose if it add or remove.
    Return returns 1 to recalculate the timeout(package added or deleted)
    or 0 to not recalculate it.
    :param data: sap message
    """
    global msg_list

    command = data.split('\n')[0]
    # RECOGIDA DEL PAYLOAD (PARTE DEL SDP)
    sdp = ""
    print (len(data.split('\n')))
    for i in range(1, len(data.split('\n'))):
        sdp = sdp + data.split('\n')[i] + "\n"

    Newmsg = sap.Message()
    Newmsg.setSource(myaddr)
    Newmsg.setPayload(sdp)


    if command == "add":

        if len(msg_list) == 0:
            hashid = add_hash()
            Newmsg.setMsgHash(hashid)

            print "msg is the first in the system\n"
            print Newmsg
            print "\n\n"
            msg_list.append(Newmsg)
            del Newmsg
            return 1

        else:
            exists = check_msg(sdp, command)

            if exists == 1:
                print "msg and newMsg are the same messages\n"
            else:
                print "msg and newMsg are different messages\n"
                hashid = add_hash()

                if hashid == "There is no connection available.":
                    print hashid
                    del Newmsg

                else:
                    Newmsg.setMsgHash(hashid)
                    msg_list.append(Newmsg)
                    del Newmsg
                    return 1

    elif command == "delete":
        print "vamos a borrar, el tamnyo ahora es ", len(msg_list)

        if len(msg_list) == 0:
            del Newmsg

        else:
            exists, hashid, msg = check_msg(sdp, command)
            if exists == 0:
                print "There is no message that is the same as the Newmsg\n"

            else:
                print "The message has been delete.\n"
                Delete_Hash(hashid, msg)
                print "despues de borrar, el tamanyo es ", len(msg_list)
                del Newmsg
        return 1


    else:
        print "The command is not correct."
        del Newmsg
    return 0


def recalculate(time_out=0, time_finish_out=0):
    """
    function to recalculate the time out.
    Time_out and time_finish_out will default to 0 if there has been a timeout in the program.
    if a package has been added or removed, timeout will be the timeout calculated previously,
    in this case return returns the recalculated time_out.
    Time_finish_out is the time at which the time_out should be activated in select
    in this case return returns the time_out and time_finish recalculated.
    """
    sum = 0

    for m in msg_list:
        # necesitamos empaquetar el mensaje para ver cuanto ocupa y recalcular el time_out
        data = m.pack()
        sum = sum + len(data)
    time_out_new = sap.tx_delay(sum/len(msg_list))
    if (time_out == 0):
        return time_out_new

    else:
        dif_time = time_out_new - time_out
        time_finish_out = time_finish_out + datetime.timedelta(seconds=dif_time)
        return time_out_new, time_finish_out

if __name__ == "__main__":

    Msg_Hash = {}

    # puts all the fields available for the hash
    for i in range(0, pow(2, 16) + 1):
        Msg_Hash.update({i: 'Available'})
    msg_list = []

    #####################
    ##TCP DATA RECEPTION#
    #####################
    # Perpare the socket RX
    sock_rx_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    sock_rx_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock_rx_tcp.bind(("", 4141)) # TODO poner puerto
    sock_rx_tcp.listen(5)
    mreq = struct.pack("4sl", socket.inet_aton(sap.DEF_ADDR), socket.INADDR_ANY)

    inputs = [sock_rx_tcp]
    # to know if there is a tcp client connected
    current_tcpclient = 0

    ###################
    ##DATA TRANSMITTE##
    ###################
    ## Prepare the socket TX
    sock_tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock_tx.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, sap.DEF_TTL)
    myaddr = socket.gethostbyname(socket.gethostname())


    # begin of time
    beginning_time = datetime.datetime.now()
    time_out=8 # TODO hay que cambiarlo
    while True:

        # select will wake up when data enters or the time_out runs out
        readable, writable, exceptional = select.select(inputs, [], [], time_out)
        print "el time out es ", time_out

        # calculation of times
        time_until_now = (datetime.datetime.now() - beginning_time).seconds #tiempo hasta ahora
        time_finish_out = datetime.datetime.now() + datetime.timedelta(seconds=time_until_now)

        # to know if the package will be sent
        send_packet = False

        # if data enters
        if len(readable) != 0:
            if current_tcpclient == 0 and readable[0] == sock_rx_tcp:

                connection_tcp, client_address_tcp = sock_rx_tcp.accept()
                inputs.append(connection_tcp)
                current_tcpclient = 1
                print "conexion tcp", connection_tcp

            # if the data that comes in comes from the socket
            if connection_tcp in readable:
                try:
                    # reception of data
                    data = connection_tcp.recv(4096)

                    if data != '':
                        # to know if the command is correct or not and to know if you
                        # have to recalculate the time
                        ret_value = tcp_handler(data)

                        if ret_value == 1:
                            connection_tcp.send("Code: 200. OK ...")
                        else:
                            connection_tcp.send("Code: 400. Error ... command error")

                        connection_tcp.close()
                        current_tcpclient = 0
                        inputs.remove(connection_tcp)

                    print datetime.datetime.now() #todo borrar

                    #
                    if ret_value == 1 and len(msg_list)!=0:
                        # to recalculate time out
                        time_out, time_finish_out = recalculate(time_out, time_finish_out)

                    # If the current time is longer than time_finish it means that the
                    # time_out is over and you must send the list.
                    # Else the waiting time is recalculated.
                    if time_finish_out > datetime.datetime.now():

                        time_out = timeturn(time_finish_out, datetime.datetime.now())
                    else:
                        send_packet = True

                except socket.timeout, e:  # socket o sock_rx_tcp

                    err = e.args[0]
                    if err == 'timed out':
                        print 'recv timed out'
                        continue
                    else:
                        pass
                        # sys.exit(1)

                    inputs = [sock_rx_tcp]

        print "El tamanyo de lista es", len(msg_list) #todo quitar
        # todo quitar el envio=True cuando se hagan pruebas reales
        send_packet = True

        # if in select the timeout is over
        if not (readable or writable or exceptional) or send_packet==True:
            print "timeout agotado"


            if len(msg_list) != 0:
                send_info()
                time_out = recalculate()

            else:
                print "There is no package to send. \n"
                pass