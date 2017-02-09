""" an agent that listen on tcp port and report vnstat json """

import multiprocessing as mp
import socket
import vnstat

PORT = 1234
PID_FILE = '/var/run/pyvnstat.pid'
LISTEN_BACKLOG = 5

def send_data(sock):
    """send json data back to client and close connection"""
    data = vnstat.read()
    sock.sendall(str(data).encode())
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()
    del sock

def listen(address, port):
    """listen for connections"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((address, port))
        sock.listen(LISTEN_BACKLOG)
        while True:
            new_connection, address = sock.accept()
            send_data(new_connection)
            # fix me : need logging address
    except Exception as error: # fix me too general exceptions catch
        print(error)
    finally:
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
        del sock

