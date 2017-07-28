#!/usr/bin/python3
""" an agent that listen on tcp port and report vnstat json """
import sys
import os
from argparse import ArgumentParser
import socketserver
import multiprocessing as mp
import vnstat

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

def get_options():
    """ process command line options """
    parser = ArgumentParser()
    parser.add_argument('-a', '--address', dest='address', default='0.0.0.0',
                        help='bind address')
    parser.add_argument('-p', '--port', dest='port', default=1234, type=int,
                        help='listening port')
    parser.add_argument('-d', '--daemon', dest='daemon', default=False,
                        action='store_true', help='run in background')
    return parser.parse_args()

def main():
    """ main function that pars args """
    options = get_options()
    if options.daemon:
        daemonize()
    start_server(options.address, options.port)


if __name__ == '__main__':
    main()

