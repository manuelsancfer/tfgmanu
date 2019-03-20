#!/usr/bin/env python

import datetime
import select
import time

import sap
import socket
import struct

msg_list = []
dictionary = {}

if __name__ == "__main__":
    # Perpare the socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", sap.DEF_PORT))
    mreq = struct.pack("4sl", socket.inet_aton(sap.DEF_ADDR), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    garbage_collector_period = 5

    while True:

        #data = sock.recv(4096)
        #msg = sap.Message()
        #msg.unpack(data)

        inputs = [sock]

        #   sock.setblocking(0)
        outputs = []
        message_queues = {}

        #readable, writable, exceptional = select.select(inputs, inputs, [], garbage_collector_period)
        readable, writable, exceptional = select.select(inputs, [], [], garbage_collector_period)
        #read = select.select(inputs, inputs, [], sock.settimeout(0))



        if len(readable)!=0:
            data = sock.recv(4096)
            msg = sap.Message()
            msg.unpack(data)

            print "time in", data

        #if not (readable or writable or exceptional):

        #msg.setAverage_time(2)

        #msg.pack()
        #print "tiempo recogido ",msg.gettime()

        #print "Received SAP:\n", msg

        # si la lista esta vacia se anyade automaticamente
            if len(msg_list) == 0:
                msg.setLast_timestamp(time.time())
                msg_list.append(msg)

            else:
                #se comprueba si existe el mensaje
                exist = False

                for ms in msg_list:
                    if ms==msg:
                        # si existe el mensaje no se anyadira
                        exist = True
                        ms.setLast_timestamp(time.time())

                        if ms.__eq2__(msg):
                            # si existe un mensaje igual se retorna un 1
                            print "Es un mensaje igual, no actuaria"
                        else:
                            print "Esta marcado el delete, se borra"
                            msg_list.remove(ms)
                        break


                if exist == False:
                    # si no existe ningun paquete igual se anyade
                    print "Mensaje anyadido"
                    msg.setLast_timestamp(time.time())
                    msg_list.append(msg)
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
                else:
                    print "no se borra"
            print "longitud lista es ", len(msg_list)

