'''
Created on 2013-1-17

@author: ausu
'''
import threading
import socket
from TCPHandler import GatewayTCPHandler
from SocketServer import TCPServer
from multiprocessing import Pipe

class Role(object):
    '''
    gate way role
    '''
    def __init__(self):
        
        self.processes = {}
        self.kill_mutex = threading.Lock()
        GatewayTCPHandler.role = self

    def init(self):
        addr = ('0.0.0.0', 80)
        try:
            self.server = TCPServer(addr, GatewayTCPHandler, bind_and_activate=False)
            self.server.server_bind()
            self.server.server_activate()
        except socket.error, e:
            print e
            return False
    
    def run(self):
        self.has_run = True
        self.server.serve_forever()
        
    def create_process(self):
        (p00, p10) = Pipe() # for the father
        (p01, p11) = Pipe() # for the child
        self.pipes = (p10, p11)
        child_pipes = (p01, p00)
        
            
        
        
        