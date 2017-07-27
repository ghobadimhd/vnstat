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
        # parent exit
        sys.exit(0)
    print(mp.current_process().pid)
    os.chdir('/')
    os.setsid()
    sys.stdout.flush()
    sys.stderr.flush()
    sys.stdin.close()
    sys.stdout.close()
    sys.stderr.close()

def main():
    """ main function that pars args """
    if '-d' in sys.argv:
        daemonize()
    start_server(ADDRESS, PORT)


if __name__ == '__main__':
    main()

