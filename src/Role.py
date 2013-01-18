'''
Created on 2013-1-17

@author: ausu
'''
import threading
import socket
from TCPHandler import GatewayTCPHandler
from SocketServer import TCPServer
from multiprocessing import Pipe
from ControlProcess import ControlChildProcess
from ConnectionPoolProcess import ConnectionPoolProcess
class Role(object):
    '''
    gate way role
    '''
    def __init__(self):
        
        self.processes = {}
        self.kill_mutex = threading.Lock()
        

    def init(self):
        addr = ('0.0.0.0', 80)
        try:
            GatewayTCPHandler.role = self
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
        proc = ConnectionPoolProcess(child_pipes, self.pipes) #只有一个ConnectionPool
        proc.start()
        child_pipes[0].close()
        child_pipes[1].close()
        
        ctrl = ControlChildProcess(self)
        ctrl.start()
        
        self.processes[proc.pid] = [(proc, ctrl), 0]
        return proc.pid
            
        
        
        