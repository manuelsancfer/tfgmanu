
import sap
import socket
import struct

msg_lista = []

if __name__ == "__main__":
    # Perpare the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", sap.DEF_PORT))
    mreq = struct.pack("4sl", socket.inet_aton(sap.DEF_ADDR), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    while True:
        data = sock.recv(4096)
        msg = sap.Message()
        msg.unpack(data)

        #print "Received SAP:\n", msg

        # si la lista esta vacia se anyade automaticamente
        if len(msg_lista) ==0:
            msg_lista.append(msg)

        else:

            #se comprueba si existe el mensaje
            exist = False
            for ms in msg_lista:
                if ms==msg:
                    # si existe el mensaje no se anyadira
                    exist = True
                    print "Ya existe el mensaje"


                    # todo probando para poder borrar en el cliente
                    # deberia ver si tiene el delete diferente para poder borrarlo
                    if ms.__eq2__(msg):
                        # si existe un mensaje igual se retorna un 1
                        print "Es un mensaje igual, no actuaria"
                    else:
                        print "Esta marcado el delete, se borra"
                    break

            if exist == False:
                # si no existe ningun paquete igual se anyade
                print "Mensaje anyadido"
                msg_lista.append(msg)
        print "Ready"
        for m in msg_lista:
            print "El contenido de lista ", m
        print "longitud lista", len(msg_lista)


