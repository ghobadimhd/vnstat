#!/usr/bin/python3
""" an agent that listen on tcp port and report vnstat json """
import sys
import os
import socketserver
import multiprocessing as mp
import vnstat

ADDRESS = '0.0.0.0'
PORT = 1234
PID_FILE = '/tmp/pyvnstat/agent.pid'

class ClientHandler(socketserver.StreamRequestHandler):
    """handler of request that send data to peers"""
    def handle(self):
        """send json data back to client and close connection"""
        data = vnstat.read()
        # convert data ro string and replace ' with "
        data = str(data).replace('\'', '"')
        self.wfile.write(data.encode())
        self.wfile.write(b'\r\n')
        self.finish()
        del data

def start_server(address, port):
    """listen for connections"""
    server = socketserver.TCPServer((address, port), ClientHandler)
    server.serve_forever()

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

def main():
    """ main function that pars args """
    if len(sys.argv) < 2:
        print('you should give start/stop parameter')
        return 1
    first_arg = sys.argv[1]
    if first_arg == 'start':
        return start_daemon()
    if first_arg == 'stop':
        return stop_daemon()

if __name__ == '__main__':
    main()

