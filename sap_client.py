import datetime
import time

import sap
import socket
import struct

msg_lista = []
diccionario = {}

if __name__ == "__main__":
    # Perpare the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", sap.DEF_PORT))
    mreq = struct.pack("4sl", socket.inet_aton(sap.DEF_ADDR), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    garbage_collector_period = 60

    while True:
        data = sock.recv(4096)
        msg = sap.Message()
        msg.unpack(data)
        #msg.setAverage_time(2)

        #msg.pack()
        #print "tiempo recogido ",msg.gettime()

        #print "Received SAP:\n", msg

        # si la lista esta vacia se anyade automaticamente
        if len(msg_lista) == 0:
            msg.setLast_timestamp(time.time())
            msg_lista.append(msg)

        else:
            #se comprueba si existe el mensaje
            exist = False

            for ms in msg_lista:
                if ms==msg:
                    # si existe el mensaje no se anyadira
                    exist = True
                    ms.setLast_timestamp(time.time())

                    if ms.__eq2__(msg):
                        # si existe un mensaje igual se retorna un 1
                        print "Es un mensaje igual, no actuaria"
                    else:
                        print "Esta marcado el delete, se borra"
                        msg_lista.remove(ms)
                    break


            if exist == False:
                # si no existe ningun paquete igual se anyade
                print "Mensaje anyadido"
                msg.setLast_timestamp(time.time())
                msg_lista.append(msg)
        print "Ready"
        print "longitud lista", len(msg_lista)

        for ms in msg_lista:
            # mira si hay que borrar algun paquete
            delete = ms.intervalPacket(time.time())
            if delete == 1:
                # si devuelve 1 borara el paquete
                msg_lista.remove(ms)



