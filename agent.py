""" an agent that listen on tcp port and report vnstat json """
import sys
import os
import socket
import vnstat

ADDRESS = '127.0.0.1'
PORT = 1234
PID_FILE = '/tmp/pyvnstat/agent.pid'
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
    except IOError as error: # fix me too general exceptions catch
        print(error)
    finally:
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
        del sock

def daemonize():
    """ make daemon process """
    pid = os.fork()
    if pid > 0:
        print('agent pid: ', pid)
        try:
            with open(PID_FILE, 'w') as pidfile:
                pidfile.write(str(pid))
        except IOError as error:
            print(error)
            os.remove(PID_FILE)
        sys.exit(0)
    os.chdir('/')
    os.setsid()
    sys.stdout.flush()
    sys.stderr.flush()
    sys.stdin.close()
    sys.stdout.close()
    sys.stderr.close()

def start_daemon():
    """ make daemon process and listen for connections """
    dirname = os.path.dirname(PID_FILE)
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    if os.path.exists(PID_FILE):
        with open(PID_FILE, 'r') as pidfile:
            pid = pidfile.read()
        print('agent process exists with pid: ', pid)
        return 1
    else:
        daemonize()
        listen(ADDRESS, PORT)

def stop_daemon():
    """ stop daemon """
    if os.path.exists(PID_FILE):
        with open(PID_FILE, 'r') as pidfile:
            pid = pidfile.read()
        os.kill(int(pid), 15)
        os.remove(PID_FILE)
        print('agent stopped...')
        return 0
    else:
        print('agent does not started .')
        return 1
