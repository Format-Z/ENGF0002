import sys
import socket
from time import sleep
import select
from nonblocking_readline import *

def get_sock():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as err:
        print("socket creation failed with error %s" %(err))
        sys.exit()
    return sock


def server(sock, port):
    # first we need to bind the socket to a specific port
    while True:
        try:
            sock.bind(('', port))
            break
        except OSError as err:
            # sometimes the port is still in use; wait til it's free
            print(err)
            print("waiting, will retry in 10 seconds")
            sleep(10)
    # tell the socket to listen for incoming connections
    sock.listen(1)


def accept_new_connection(sock):
    # Wait here until an incoming connection arrives. When it does,
    # accept it
    client_sock, addr = sock.accept()
    print("Got an incoming connection from ", addr)
    return client_sock

listener_sock = get_sock()
server(listener_sock, 1234)

while True:
    print("listening for incoming connection...")
    sock = accept_new_connection(listener_sock)
    close_conn = False
    while close_conn == False:
        try:
            # call select to find out if there's any data ready
            rd, wd, ed = select.select([sock, sys.stdin],[],[])
            if sys.stdin in rd:
                key_text = nonblocking_readline()
                if key_text != "":
                    encoded_text = key_text.encode('utf-8')
                    bytessent = sock.send(encoded_text)
                    print("sent ", bytessent, "bytes")

            if sock in rd:
                received_bytes = sock.recv(1024)
                if len(received_bytes) == 0:
                    close_conn = True
                else:
                    net_text = received_bytes.decode('utf-8')
                    print(">>", net_text)    
        except (EOFError, KeyboardInterrupt, BrokenPipeError):
            close_conn = True

    print("End of input, closing connection")
    sock.close()
