import sys
import socket
from time import sleep

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
    print("listening for incoming connection...")

    # Wait here until an incoming connection arrives. When it does,
    # accept it
    client_sock, addr = sock.accept()
    print("Got an incoming connection from ", addr)
    return client_sock

listener_sock = get_sock()
sock = server(listener_sock, 1234)

while True:
    try:
        encoded_text = sock.recv(1024)
    except KeyboardInterrupt as err:
        print("user termination")
        sock.close()
        break

    if len(encoded_text) == 0:
        print("connection closed by remote end")
        break
    text = encoded_text.decode('utf-8')
    print(text)
