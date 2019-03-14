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


def client(sock, ip, port):
    while True:
        try:
            print(ip, port, sock)
            sock.connect((ip, port))
            print("connected to", ip, "on port", port)
            return sock
        except ConnectionRefusedError as err:
            # server seems to not be ready for us yet.  We'll retry shortly
            # socket latches into error state, so close it and try again
            sock.close()
            sock = get_sock()
            print("waiting for server")
            sleep(1)
        except OSError as err:
            print("OSError", err)
        

sock = get_sock()
sock = client(sock, "127.0.0.1", 1234)

while True:
    try:
        text = input(">")
    except EOFError as err:
        print("End of input, closing connection")
        sock.close()
        break

    encoded_text = text.encode('utf-8')

    try:
        bytessent = sock.send(encoded_text)
        print("sent ", bytessent, "bytes")
    except BrokenPipeError as err:
        print("Connection closed by remote end")
        break
