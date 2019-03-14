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

close_conn = False
while close_conn == False:
    try:
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
